from django.contrib import admin
from ReviewAnswer.models import *

class ReviewAnswerAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None, {
                'fields': [
                    'review',
                    'review_question',
                    'text',
                ]
            }
        ),
    ]
    list_display = ('id', 'review', 'review_question', 'text' )

admin.site.register(ReviewAnswer, ReviewAnswerAdmin)