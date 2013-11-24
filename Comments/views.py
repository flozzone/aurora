from django.shortcuts import render

from django.views.generic import ListView
from Comments.models import Comment


class CommentList(ListView):
    model = Comment
