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
                    'creation_time'
                ]
            }
        ),
    ]
    list_display = ('id', 'review', 'review_question', 'text', 'creation_time' )
    readonly_fields = ("creation_time", )

admin.site.register(ReviewAnswer, ReviewAnswerAdmin)