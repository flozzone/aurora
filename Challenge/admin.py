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

class StackChallengeRelationAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None, {
                'fields': [
                    'stack',
                    'challenge'
                ]
            }
        ),
    ]
    list_display = ('id', 'stack', 'challenge', )

admin.site.register(StackChallengeRelation, StackChallengeRelationAdmin)
