from django.contrib import admin
from Review.models import *

class ReviewAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None, {
                'fields': [
                    'elaboration',
                    'submission_time',
                    'reviewer',
                ]
            }
        ),
    ]
    list_display = ('id', 'elaboration', 'submission_time', 'reviewer', )

admin.site.register(Review, ReviewAdmin)