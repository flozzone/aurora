from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET

from django.contrib.auth.decorators import login_required
from django import forms
from django.utils import timezone
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.contrib.contenttypes.models import ContentType
import json
from AuroraUser.models import AuroraUser

from Comments.models import Comment, CommentsConfig, CommentList, Vote, CommentReferenceObject
from Course.models import Course
from Notification.models import Notification
from Slides.models import Slide
from AuroraProject.settings import SECRET_KEY, LECTURER_USERNAME
from local_settings import LECTURER_SECRET


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
    course_short_title = forms.CharField(widget=forms.HiddenInput(attrs={'id': 'replyCourseShortTitle'}))
    uri = forms.CharField(widget=forms.HiddenInput, max_length=200)
    text = forms.CharField(widget=forms.Textarea(attrs={'id': 'replyTextarea'}), label='')
    visibility = forms.ChoiceField(choices=Comment.VISIBILITY_CHOICES)


@require_POST
@login_required
def post_comment(request):
    form = CommentForm(request.POST)
    try:
        create_comment(form, request)
    except ValidationError as error:
        raise error
        return HttpResponseBadRequest('The submitted form seems to be borken')
    return HttpResponse('')


@require_POST
@login_required
def delete_comment(request):
    comment_id = request.POST['comment_id']
    deleter = RequestContext(request)['user']

    comment = Comment.objects.filter(id=comment_id).select_related('parent__children')[0]

    if comment.author != deleter and not deleter.is_staff:
        return HttpResponseForbidden('You shall not delete!')

    comment.deleter = deleter
    comment.delete_date = timezone.now()
    comment.promoted = False
    comment.seen = True
    comment.save()
    CommentList.get_by_comment(comment).increment()

    return HttpResponse('')


@require_POST
@login_required
def post_reply(request):
    form = ReplyForm(request.POST)
    try:
        create_comment(form, request)
    except ValidationError:
        return HttpResponseBadRequest('The submitted form seems to be borken')
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
    comment.edited_date = timezone.now()
    comment.save()
    CommentList.get_by_comment(comment).increment()

    return HttpResponse('')


@csrf_exempt
@require_POST
def lecturer_post(request):
    data = request.POST
    if data['secret'] != LECTURER_SECRET:
        return HttpResponseForbidden('You shall not pass!')

    user = AuroraUser.objects.get(username=LECTURER_USERNAME)
    ref_obj = Slide.objects.get(filename=data['filename'])

    Comment.objects.create(text=data['text'],
                           author=user,
                           content_object=ref_obj,
                           parent=None,
                           post_date=timezone.now(),
                           visibility=Comment.PUBLIC)

    return HttpResponse('')


def create_comment(form, request):
    if not form.is_valid():
        raise ValidationError('The submitted form was not valid')

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

    if comment.visibility == Comment.PRIVATE:
        comment.seen = True
        comment.save()

    comment_list = CommentList.get_by_comment(comment)

    if comment_list.uri is None or 'evaluation' in comment_list.uri:
        comment_list.uri = form.cleaned_data['uri']
        comment_list.save()

    comment_list.increment()

    if comment.visibility == Comment.PRIVATE:
        return

    if parent_comment is None:
        return

    if parent_comment.author == comment.author:
        return

    if comment.visibility == Comment.STAFF and not parent_comment.author.is_staff:
        return

    course_short_title = form.cleaned_data['course_short_title']

    if course_short_title != "":
        course = Course.get_or_raise_404(course_short_title)
        link = comment_list.uri + '#comment_' + str(parent_comment.id)
    else:
        course = None
        link = ""

    text = comment.author.nickname[:15] + ': '
    if len(comment.text) > 50:
        text += comment.text[:47] + "..."
    else:
        text += comment.text[:50]

    obj, created = Notification.objects.get_or_create(
        user=parent_comment.author,
        course=course,
        text=text,
        image_url=comment.author.avatar.url,
        link=link
    )

    if not created:
        obj.creation_time = timezone.now()
        obj.read = False
        obj.save()


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
def mark_seen(request):
    requester = RequestContext(request)['user']

    if not requester.is_staff:
        return HttpResponseForbidden('Only staff may seen this!')

    key, comment_ids = next(request.POST.lists())

    if not key == "comment_ids[]":
        return HttpResponseBadRequest('No comment ids provided')

    for comment_id in comment_ids:
        try:
            comment = Comment.objects.get(id=comment_id)
            comment.seen = True
            comment.save()
        except Comment.DoesNotExist:
            continue

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


@require_POST
@login_required
def update_comments(request):
    polling_active, polling_idle = CommentsConfig.get_polling_interval()

    response_data = {'polling_active_interval': polling_active,
                     'polling_idle_interval': polling_idle}

    client_revisions = unpack_revisions(request.POST)

    comment_lists = []
    for client_revision in client_revisions:
        comment_list = get_comment_list_update(request, client_revision)
        if comment_list is not None:
            comment_lists.append(comment_list)

    response_data.update({'comment_list_updates': comment_lists})
    template_response = json.dumps(response_data)
    return HttpResponse(template_response, content_type="application/json")

@require_GET
@login_required
def comment_list_page(request):
    client_revision = {
        'number': -1,
        'ref_id': request.GET['ref_id'],
        'ref_type': request.GET['ref_type']
    }

    template = 'Comments/comment_list_page.html'
    rendered_response = get_comment_list_update(request, client_revision, template)['comment_list']

    return HttpResponse(rendered_response)


def get_comment_list_update(request, client_revision, template='Comments/comment_list.html'):
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
                   'revision': revision,
                   'request': request}

        return {
            'ref_id': ref_id,
            'ref_type': ref_type,
            'comment_list': render_to_string(template, context)
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


# TODO is this just a test method? (delete or mark if yes)
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
