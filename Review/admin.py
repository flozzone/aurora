from django.contrib import admin
from Review.models import *

class ReviewAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None, {
                'fields': [
                    'elaboration',
                    'creation_time',
                    'submission_time',
                    'reviewer',
                ]
            }
        ),
    ]
    list_display = ('id', 'elaboration', 'creation_time', 'submission_time', 'reviewer', )
    readonly_fields = ("creation_time", )

admin.site.register(Review, ReviewAdmin)