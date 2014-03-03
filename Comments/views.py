from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST, require_GET

from django.contrib.auth.decorators import login_required
from django import forms
from django.utils import timezone
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.contrib.contenttypes.models import ContentType
import json

from Comments.models import Comment, CommentsConfig, CommentList, Vote
from Notification.models import Notification
from Comments.tests import CommentReferenceObject


# class BookmarkedView(ListView):
#     queryset = Comment.query_bookmarked()
#
    # def get_context_data(self, **kwargs):
    #     context = super(BookmarkedView, self).get_context_data(**kwargs)
    #     context['form'] = CommentForm()
        # context['reply_form'] = ReplyForm()
        # context['form_action'] = '/post/'
        # return context


class CommentForm(forms.Form):
    reference_type_id = forms.IntegerField(widget=forms.HiddenInput)
    reference_id = forms.IntegerField(widget=forms.HiddenInput)
    uri = forms.CharField(widget=forms.HiddenInput, max_length=200)
    text = forms.CharField(widget=forms.Textarea(attrs={'id': 'commentTextarea'}), label='')
    visibility = forms.ChoiceField(choices=Comment.VISIBILITY_CHOICES)


class ReplyForm(forms.Form):
    reference_type_id = forms.IntegerField(widget=forms.HiddenInput)
    reference_id = forms.IntegerField(widget=forms.HiddenInput)
    parent_comment = forms.IntegerField(widget=forms.HiddenInput)
    uri = forms.CharField(widget=forms.HiddenInput, max_length=200)
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
    CommentList.get_by_comment(comment).increment()

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

    if comment.author != requester:
        return HttpResponseForbidden('You shall not edit!')

    text = data['text']
    if text == '':
        return HttpResponse('')

    comment.text = data['text']
    comment.save()
    CommentList.get_by_comment(comment).increment()

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

        comment_list = CommentList.get_by_comment(comment)
        comment_list.uri = form.cleaned_data['uri']
        comment_list.save()

        comment_list.increment()

        if parent_comment is not None and parent_comment.author != comment.author:
            obj, created = Notification.objects.get_or_create(
                user=parent_comment.author,
                course=context['last_selected_course'],
                text=Notification.NEW_MESSAGE + "You've received a reply to one of your comments",
                image_url=comment.author.avatar.url,
                link=comment_list.uri
            )

            if not created:
                obj.creation_time = timezone.now()
                obj.read = False
                obj.save()

        # if parent_comment is not None:
        #     if ref_obj_model == Elaboration:
        #         elaboration = ref_obj
        #         user = parent_comment.author
        #         obj, created = Notification.objects.get_or_create(
        #             user=user,
        #             course=context['last_selected_course'],
        #             text=Notification.NEW_MESSAGE + elaboration.challenge.title,
        #             image_url=elaboration.challenge.image.url,
        #             link="challenge=" + str(elaboration.challenge.id)
        #         )


@require_POST
@login_required
def vote_on_comment(request):
    data = request.POST

    comment = Comment.objects.get(id=data['comment_id'])
    user = RequestContext(request)['user']

    if user == comment.author:
        return HttpResponseForbidden('')

    if data['direction'] == 'up':
        vote_up_on(comment, user)
    elif data['direction'] == 'down':
        vote_down_on(comment, user)

    return HttpResponse('')


def vote_up_on(comment, voter):
    try:
        vote = comment.votes.get(voter=voter)
        if vote.direction == Vote.DOWN:
            vote.delete()
            CommentList.get_by_comment(comment).increment()

        return
    except Vote.DoesNotExist:
        Vote.objects.create(direction=Vote.UP, voter=voter, comment=comment)
        CommentList.get_by_comment(comment).increment()


def vote_down_on(comment, voter):
    try:
        vote = comment.votes.get(voter=voter)
        if vote.direction == Vote.UP:
            vote.delete()
            CommentList.get_by_comment(comment).increment()

        return
    except Vote.DoesNotExist:
        Vote.objects.create(direction=Vote.DOWN, voter=voter, comment=comment)
        CommentList.get_by_comment(comment).increment()


@require_POST
@login_required
def bookmark_comment(request):
    data = request.POST

    requester = RequestContext(request)['user']

    try:
        comment = Comment.objects.get(id=data['comment_id'])
    except Comment.DoesNotExist:
        return HttpResponse('')

    if data['bookmark'] == 'true':
        comment.bookmarked_by.add(requester)
    else:
        comment.bookmarked_by.remove(requester)

    comment.save()
    CommentList.get_by_comment(comment).increment()

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
    CommentList.get_by_comment(comment).increment()

    return HttpResponse('')


@require_GET
@login_required
def update_comments(request):
    polling_active, polling_idle = CommentsConfig.get_polling_interval()

    response_data = {'polling_active_interval': polling_active,
                     'polling_idle_interval': polling_idle}

    client_revisions = unpack_revisions(request.GET)

    comment_lists = []
    for client_revision in client_revisions:
        comment_list = get_comment_list_update(request, client_revision)
        if comment_list is not None:
            comment_lists.append(comment_list)

    response_data.update({'comment_list_updates': comment_lists})
    template_response = json.dumps(response_data)
    return HttpResponse(template_response, content_type="application/json")


def get_comment_list_update(request, client_revision):
    ref_type = client_revision['ref_type']
    ref_id = client_revision['ref_id']
    user = RequestContext(request)['user']

    revision = CommentList.get_by_ref_numbers(ref_id, ref_type).revision

    if revision > int(client_revision['number']):
        comment_list = Comment.query_top_level_sorted(ref_id, ref_type, user)
        id_suffix = "_" + str(ref_id) + "_" + str(ref_type)

        context = {'comment_list': comment_list,
                   'ref_type': ref_type,
                   'ref_id': ref_id,
                   'id_suffix': id_suffix,
                   'requester': user,
                   'revision': revision}

        return {
            'ref_id': ref_id,
            'ref_type': ref_type,
            'comment_list': render_to_string('Comments/comment_list.html', context)
        }
    return None


def unpack_revisions(revisions):
    keys = revisions.keys()
    revisions_array = []
    i = 0
    while True:
        if 'revisions[' + str(i) + '][number]' not in keys:
            break
        revisions_array.append({
            'number': revisions['revisions[' + str(i) + '][number]'],
            'ref_id': revisions['revisions[' + str(i) + '][ref_id]'],
            'ref_type': revisions['revisions[' + str(i) + '][ref_type]']
        })
        i += 1

    return revisions_array


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


@login_required
def bookmarks(request):
    requester = RequestContext(request)['user']
    comment_list = Comment.query_bookmarks(requester)
    template = 'Comments/bookmarks_list.html'
    return render_to_response(template, {'comment_list': comment_list}, context_instance=RequestContext(request))
