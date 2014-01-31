from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST, require_GET

from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django import forms
from django.utils import timezone
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.contrib.contenttypes.models import ContentType
import json

from Comments.models import Comment, CommentsConfig, CommentListRevision
from Elaboration.models import Elaboration
from Notification.models import Notification
from Comments.tests import CommentReferenceObject


class CommentForm(forms.Form):
    reference_type_id = forms.IntegerField(widget=forms.HiddenInput)
    reference_id = forms.IntegerField(widget=forms.HiddenInput)
    text = forms.CharField(widget=forms.Textarea(attrs={'id': 'commentTextarea'}), label='')
    visibility = forms.ChoiceField(choices=Comment.VISIBILITY_CHOICES)


class ReplyForm(forms.Form):
    reference_type_id = forms.IntegerField(widget=forms.HiddenInput)
    reference_id = forms.IntegerField(widget=forms.HiddenInput)
    parent_comment = forms.IntegerField(widget=forms.HiddenInput)
    text = forms.CharField(widget=forms.Textarea(attrs={'id': 'replyTextarea'}), label='')
    visibility = forms.ChoiceField(choices=Comment.VISIBILITY_CHOICES)


@require_POST
@login_required
def post_comment(request):
    form = CommentForm(request.POST)
    create_comment(form, request)
    return HttpResponse('')


@require_POST
@login_required
def delete_comment(request):
    comment_id = request.POST['comment_id']
    deleter = RequestContext(request)['user']

    comment = Comment.objects.get(id=comment_id)

    if comment.author != deleter and not deleter.is_staff:
        return HttpResponseForbidden('You shall not delete!')

    comment.deleter = deleter
    comment.delete_date = timezone.now()
    comment.save()
    CommentListRevision.get_by_comment(comment).increment()

    return HttpResponse('')


@require_POST
@login_required
def post_reply(request):
    form = ReplyForm(request.POST)
    create_comment(form, request)
    return HttpResponse('')


@require_POST
@login_required
def edit_comment(request):
    data = request.POST
    context = RequestContext(request)
    requester = context['user']

    try:
        comment = Comment.objects.get(id=data['comment_id'])
    except Comment.DoesNotExist:
        return HttpResponse('')

    if comment.author != requester and not requester.is_staff:
        return HttpResponseForbidden('You shall not edit!')

    text = data['text']
    if text == '':
        return HttpResponse('')

    comment.text = data['text']
    comment.save()
    CommentListRevision.get_by_comment(comment).increment()

    return HttpResponse('')


def create_comment(form, request):
    if form.is_valid():
        context = RequestContext(request)
        user = context['user']
        ref_type_id = form.cleaned_data['reference_type_id']
        ref_obj_id = form.cleaned_data['reference_id']
        ref_obj_model = ContentType.objects.get_for_id(ref_type_id).model_class()
        ref_obj = ref_obj_model.objects.get(id=ref_obj_id)
        visibility = form.cleaned_data['visibility']

        parent_comment_id = form.cleaned_data.get('parent_comment', None)
        if parent_comment_id is not None:
            try:
                parent_comment = Comment.objects.get(id=parent_comment_id)
            except ObjectDoesNotExist:
                parent_comment = None
        else:
            parent_comment = None

        comment = Comment.objects.create(text=form.cleaned_data['text'],
                                         author=user,
                                         content_object=ref_obj,
                                         parent=parent_comment,
                                         post_date=timezone.now(),
                                         visibility=visibility)

        comment.save()
        CommentListRevision.get_by_comment(comment).increment()

        if parent_comment is not None:
            if ref_obj_model == Elaboration:
                elaboration = ref_obj
                user = parent_comment.author
                obj, created = Notification.objects.get_or_create(
                    user=user,
                    course=context['last_selected_course'],
                    text=Notification.NEW_MESSAGE + elaboration.challenge.title,
                    image_url='/static/img/' + elaboration.challenge.image_url,
                    link="challenge=" + str(elaboration.challenge.id)
                )


@login_required
def vote_on_comment(request):
    data = request.GET
    if data['direction'] == 'up':
        diff = 1
    elif data['direction'] == 'down':
        diff = -1
    else:
        return HttpResponse('')

    comment = Comment.objects.get(id=data['comment_id'])
    user = RequestContext(request)['user']

    if user == comment.author:
        return HttpResponseForbidden('')

    if comment.was_voted_on_by.filter(pk=user.id).exists():
        return HttpResponseForbidden('')

    comment.score += diff
    comment.was_voted_on_by.add(user)
    comment.save()
    CommentListRevision.get_by_comment(comment).increment()

    return HttpResponse('')


@require_POST
@login_required
def bookmark_comment(request):
    data = request.POST

    requester = RequestContext(request)['user']

    try:
        comment = Comment.objects.get(id=data['comment_id'])
    except Comment.DoesNotExist:
        return HttpResponse('')

    if data['value'] == 'true':
        comment.bookmarked_by.add(requester)
    else:
        comment.bookmarked_by.remove(requester)

    comment.save()
    CommentListRevision.get_by_comment(comment).increment()

    return HttpResponse('')


@require_POST
@login_required
def promote_comment(request):
    data = request.POST

    requester = RequestContext(request)['user']
    if not requester.is_staff:
        return HttpResponseForbidden('You shall not promote!')

    try:
        comment = Comment.objects.get(id=data['comment_id'])
    except Comment.DoesNotExist:
        return HttpResponse('')

    comment.promoted = True if data['value'] == 'true' else False
    comment.save()
    CommentListRevision.get_by_comment(comment).increment()

    return HttpResponse('')


@require_GET
@login_required
def update_comments(request):
    client_revision = request.GET
    ref_type = client_revision['ref_type']
    ref_id = client_revision['ref_id']
    user = RequestContext(request)['user']

    revision = CommentListRevision.get_by_ref_numbers(ref_id, ref_type).number

    polling_interval = CommentsConfig.get_polling_interval()

    if revision > int(client_revision['id']):
        comment_list = Comment.query_top_level_sorted(ref_id, ref_type, user)
        id_suffix = "_" + str(ref_id) + "_" + str(ref_type)

        context = {'comment_list': comment_list,
                   'ref_type': ref_type,
                   'ref_id': ref_id,
                   'id_suffix': id_suffix,
                   'requester': user,
                   'revision': revision}
        template_response = json.dumps({
            'comment_list': render_to_string('Comments/comment_list.html', context),
            'polling_interval': polling_interval
        })
            # render_to_response('Comments/comment_list.html', context))
        return HttpResponse(template_response, content_type="application/json")
    else:
        return HttpResponse(json.dumps({
            'polling_interval': polling_interval
        }))


@login_required
def feed(request):
    try:
        o = CommentReferenceObject.objects.get(id=1)
        o2 = CommentReferenceObject.objects.get(id=2)
    except CommentReferenceObject.DoesNotExist:
        CommentReferenceObject().save()
        o = CommentReferenceObject.objects.get(id=1)
        CommentReferenceObject().save()
        o2 = CommentReferenceObject.objects.get(id=2)
    return render(request, 'Comments/feed.html', {'object': o, 'object2': o2})
