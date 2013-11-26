from django.shortcuts import render

from django.views.generic import ListView
from Comments.models import Comment
from django.contrib.auth.decorators import login_required


class CommentList(ListView):
    #model = Comment
    queryset = Comment.objects.order_by('-post_date')

    def get_context_data(self, **kwargs):
        context = super(CommentList, self).get_context_data(**kwargs)
        context['foo'] = 'krawuzikabuzi'
        return context
