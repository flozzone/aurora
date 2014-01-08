from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.http import require_POST, require_GET

from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django import forms
from django.utils import timezone
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.contenttypes.models import ContentType

from Comments.models import Comment
from PortfolioUser.models import PortfolioUser
from Comments.tests import CommentReferenceObject
import json


class CommentList(ListView):
    queryset = Comment.objects.filter(parent=None).order_by('-post_date')

    def get_context_data(self, **kwargs):
        context = super(CommentList, self).get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['form_action'] = '/post/'
        return context


class CommentForm(forms.Form):
    reference_type_id = forms.IntegerField(widget=forms.HiddenInput)
    reference_id = forms.IntegerField(widget=forms.HiddenInput)
    text = forms.CharField(widget=forms.Textarea(attrs={'id': 'commentText'}), label='')


@require_POST
@login_required
def post_comment(request):
    form = CommentForm(request.POST)
    if form.is_valid():
        user = PortfolioUser.objects.get(id=request.user.id)
        ref_type_id = form.cleaned_data['reference_type_id']
        ref_obj_id = form.cleaned_data['reference_id']
        ref_obj_model = ContentType.objects.get_for_id(ref_type_id).model_class()
        ref_obj = ref_obj_model.objects.get(id=ref_obj_id)
        comment = Comment.objects.create(text=form.cleaned_data['text'],
                                         author=user,
                                         content_object=ref_obj,
                                         post_date=timezone.now())
        comment.save()
        data = {'author': comment.author.username,
                # 'post_date': comment.post_date,
                'text': comment.text}
    #return HttpResponse(json.dumps(data), content_type="application/json")
    return render_to_response('Comments/comment.html', {'comment': comment}, context_instance = RequestContext(request))
    #return HttpResponseRedirect(reverse('Comments:feed'))


@require_GET
@login_required
def update_comment(request):
    print(request.GET)


def feed(request):
    try:
        o = CommentReferenceObject.objects.get(id=1)
    except CommentReferenceObject.DoesNotExist:
        CommentReferenceObject().save()
        o = CommentReferenceObject.objects.get(id=1)
    return render(request, 'Comments/feed.html', {'object': o})


def test_template_tags(request):
    o = CommentReferenceObject.objects.all()[0]
    #return render(request, 'Comments/test_template_tags.html', {'object': o})
    return render_to_response('Comments/test_template_tags.html', {'object': o}, context_instance=RequestContext(request))
