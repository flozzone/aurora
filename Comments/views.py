from django.core.urlresolvers import reverse
from django.shortcuts import render

from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django import forms
from django.utils import timezone
from django.http import HttpResponseRedirect

from Comments.models import Comment
from PortfolioUser.models import PortfolioUser


class CommentList(ListView):
    #queryset = Comment.objects.order_by('-post_date')
    queryset = Comment.objects.filter(parent=None).order_by('-post_date')

    def get_context_data(self, **kwargs):
        context = super(CommentList, self).get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['form_action'] = '/post/'
        return context


class CommentForm(forms.Form):
    reference_type = forms.CharField(widget=forms.HiddenInput)
    reference_pk = forms.CharField(widget=forms.HiddenInput)
    text = forms.CharField(widget=forms.Textarea, label='')


# TODO do some more reading on csrf protection, maybe use csrf required decorator
@login_required
def post_comment(request):
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            user = PortfolioUser.objects.filter(id=request.user.id)[0]
            #TODO user = PortfolioUser.objects.get(id=request.user.id) is better
            print("=== handmade debug:")
            print(form.reference_pk)
            print(form.reference_type)
            #comment = Comment.objects.create(text=form.cleaned_data['text'], author=user, post_date=timezone.now())
            #comment.save()
    return HttpResponseRedirect(reverse('Comments:feed'))


def test_template_tags(request):
    from tests import dummy_user_generator
    from PortfolioUser import models

    u1 = dummy_user_generator()
    u1.save()
    return render(request, 'Comments/test_template_tags.html', {object: u1})
