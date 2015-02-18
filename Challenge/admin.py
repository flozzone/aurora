from django.contrib import admin
from Challenge.models import *

class ChallengeAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None, {
                'fields': [
                    'title',
                    'subtitle',
                    'prerequisite',
                    'description',
                    'image',
                    'accepted_files',
                    'course'
                ]
            }
        ),
    ]
    list_display = ('id', 'title', 'subtitle', 'prerequisite', 'description', 'image', 'accepted_files', )

admin.site.register(Challenge, ChallengeAdmin)

