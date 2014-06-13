from django.contrib import admin
from Elaboration.models import *

class ElaborationAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None, {
                'fields': [
                    'challenge',
                    'user',
                    'creation_time',
                    'elaboration_text',
                    'submission_time',
                ]
            }
        ),
    ]
    list_display = ('id', 'challenge', 'user', 'creation_time', 'elaboration_text', 'submission_time', )
    search_fields = ('user__username',)
    readonly_fields = ("creation_time",)

admin.site.register(Elaboration, ElaborationAdmin)