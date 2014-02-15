from django.contrib import admin
from Comments.models import Comment, CommentsConfig

class CommentAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None, {
                'fields': [
                    'text',
                    'author',
                    'post_date',
                    'delete_date',
                    'deleter',
                    'parent',
                    'promoted',
                    'content_type',
                    'object_id',
                ]
            }
        ),
    ]
    list_display = ('id', 'text', 'author', 'post_date', 'delete_date', 'deleter', 'parent', 'promoted', 'content_type', 'object_id', )

admin.site.register(Comment, CommentAdmin)


class CommentsConfigAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None, {
                'fields': [
                    'key',
                    'value',
                ]
            }
        ),
    ]
    list_display = ('key', 'value', )

admin.site.register(CommentsConfig, CommentsConfigAdmin)