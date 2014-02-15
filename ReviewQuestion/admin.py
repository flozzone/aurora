from django.contrib import admin
from ReviewQuestion.models import *

class ReviewQuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None, {
                'fields': [
                    'challenge',
                    'order',
                    'text',
                    'boolean_answer',
                    'visible_to_author',
                ]
            }
        ),
    ]
    list_display = ('id', 'challenge', 'order', 'text', 'boolean_answer', 'visible_to_author', )

admin.site.register(ReviewQuestion, ReviewQuestionAdmin)