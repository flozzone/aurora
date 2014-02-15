from django.contrib import admin
from Elaboration.models import *

class ElaborationAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None, {
                'fields': [
                    'user',
                    'elaboration_text',
                    'submission_time',
                ]
            }
        ),
    ]
    list_display = ('id', 'user', 'elaboration_text', 'submission_time', )

admin.site.register(Elaboration, ElaborationAdmin)