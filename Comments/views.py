from django.core.urlresolvers import reverse
from django.shortcuts import render

from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django import forms
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType

from Comments.models import Comment
from PortfolioUser.models import PortfolioUser
from Comments.tests import CommentReferenceObject


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
    text = forms.CharField(widget=forms.Textarea, label='')


@login_required
def post_comment(request):
    if request.method == 'POST':
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
    return HttpResponseRedirect(reverse('Comments:feed'))


def feed(request):
    o = CommentReferenceObject.objects.get(1)
    return render(request, 'Comments/feed.html', {'object': o})

def test_template_tags(request):
    o = CommentReferenceObject.objects.all()[0]
    return render(request, 'Comments/test_template_tags.html', {'object': o})
