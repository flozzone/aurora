from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.http import require_POST, require_GET

from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django import forms
from django.utils import timezone
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.contrib.contenttypes.models import ContentType

from Comments.models import Comment
from PortfolioUser.models import PortfolioUser
from Comments.tests import CommentReferenceObject


class CommentList(ListView):
    queryset = Comment.objects.filter(parent=None).order_by('-post_date')

    def get_context_data(self, **kwargs):
        context = super(CommentList, self).get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['reply_form'] = ReplyForm()
        # context['form_action'] = '/post/'
        return context


class CommentForm(forms.Form):
    reference_type_id = forms.IntegerField(widget=forms.HiddenInput)
    reference_id = forms.IntegerField(widget=forms.HiddenInput)
    visibility = forms.ChoiceField(choices=Comment.VISIBILITY_CHOICES)
    text = forms.CharField(widget=forms.Textarea(attrs={'id': 'commentTextarea'}), label='')


class ReplyForm(forms.Form):
    reference_type_id = forms.IntegerField(widget=forms.HiddenInput)
    reference_id = forms.IntegerField(widget=forms.HiddenInput)
    visibility = forms.ChoiceField(choices=Comment.VISIBILITY_CHOICES)
    parent_comment = forms.IntegerField(widget=forms.HiddenInput)
    text = forms.CharField(widget=forms.Textarea(attrs={'id': 'replyTextarea'}), label='')


@require_POST
@login_required
def post_comment(request):
    form = CommentForm(request.POST)
    handle_form(form, request)
    # #return HttpResponse(json.dumps(data), content_type="application/json")
    # # return render_to_response('Comments/comment.html', {'comment': comment}, context_instance=RequestContext(request))
    return HttpResponse('')
    #return HttpResponseRedirect(reverse('Comments:feed'))


@require_POST
@login_required
def delete_comment(request):
    comment_id = request.POST['comment_id']
    deleter = PortfolioUser.objects.get(id=request.user.id)

    comment = Comment.objects.get(id=comment_id)

    if comment.author != deleter and not deleter.is_staff:
        return HttpResponseForbidden('You shall not delete (other users posts)!')

    parent = comment.parent

    # delete comment tree for comment without non-deleted responses
    if parent is None:
        if comment.responses().filter(deleter=None).count() == 0:
            comment.delete_with_responses()
            return HttpResponse('')
    else:
        if parent.deleter is not None:
            non_deleted_responses = parent.responses().filter(deleter=None).exclude(id=comment_id).count()
            if non_deleted_responses == 0:
                parent.delete_with_responses()
                return HttpResponse('')

    comment.text = '[deleted]'
    comment.deleter = deleter
    comment.delete_date = timezone.now()
    comment.save()

    return HttpResponse('')


@require_POST
@login_required
def post_reply(request):
    form = ReplyForm(request.POST)
    handle_form(form, request)
    return HttpResponse('')


def handle_form(form, request):
    if form.is_valid():
        user = PortfolioUser.objects.get(id=request.user.id)
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
    user = PortfolioUser.objects.get(id=request.user.id)

    if user == comment.author:
        return HttpResponseForbidden('')

    if comment.was_voted_on_by.filter(pk=request.user.id).exists():
        return HttpResponseForbidden('')

    comment.score += diff
    comment.was_voted_on_by.add(user)
    comment.save()

    return HttpResponse('')


@require_GET
@login_required
def update_comments(request):
    latest_client_comment = request.GET
    ref_type = latest_client_comment['ref_type']
    ref_id = latest_client_comment['ref_id']
    user = PortfolioUser.objects.get(id=request.user.id)

    try:
        latest_comment_id = Comment.query_all(ref_id, ref_type, user).latest('id').id
    except ObjectDoesNotExist:
        latest_comment_id = -1

    if int(latest_client_comment['id']) < int(latest_comment_id):
        comment_list = Comment.query_top_level_sorted(ref_id, ref_type, user)
        id_suffix = "_" + str(ref_id) + "_" + str(ref_type)
        context = {'comment_list': comment_list,
                   'ref_type': ref_type,
                   'ref_id': ref_id,
                   'id_suffix': id_suffix,
                   'requester': user}
        return render_to_response('Comments/comment_list.html', context)
    else:
        return HttpResponse('')


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


def test_template_tags(request):
    o = CommentReferenceObject.objects.all()[0]
    #return render(request, 'Comments/test_template_tags.html', {'object': o})
    return render_to_response('Comments/test_template_tags.html', {'object': o}, context_instance=RequestContext(request))
