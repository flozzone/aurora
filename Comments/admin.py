from django.contrib import admin
from Comments.models import Comment, CommentsConfig

admin.site.register(Comment)
admin.site.register(CommentsConfig)
