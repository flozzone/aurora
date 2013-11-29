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
#    model = Comment
    queryset = Comment.objects.order_by('-post_date')

    def get_context_data(self, **kwargs):
        context = super(CommentList, self).get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['form_action'] = '/post/'
        return context


class CommentForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea, label='New comment')


class ContactForm(forms.Form):
    subject = forms.CharField(max_length=100)
    message = forms.CharField()
    sender = forms.EmailField()
    cc_myself = forms.BooleanField(required=False)


def contact(request):
    if request.method == 'POST':  # If the form has been submitted...
        form = ContactForm(request.POST) # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            print(form.cleaned_data)
            # Process the data in form.cleaned_data
            # ...
            return HttpResponseRedirect('/contact/')  # Redirect after POST
    else:
        form = ContactForm()  # An unbound form

    return render(request, 'Comments/contact.html', {
        'form': form,
    })


def post(request):
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            user = PortfolioUser.objects.filter(id=request.user.id)[0]
            # TODO authentication + authorization!
            comment = Comment.objects.create(text=form.cleaned_data['text'], author=user, post_date=timezone.now())
            comment.save()
    return HttpResponseRedirect(reverse('Comments:feed'))
