from django.contrib import admin
from AuroraUser.models import *

class AuroraUserAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None, {
                'fields': [
                    'nickname',
                    'last_activity',
                    'statement',
                    'upload_path',
                    'avatar',
                    'oid',
                    'tags',
                    'matriculation_number',
                    'study_code',
                ]
            }
        ),
    ]
    list_display = ('id', 'nickname', 'last_activity', 'statement', 'upload_path', 'avatar', 'oid', 'tags', 'matriculation_number', 'study_code', )
    readonly_fields = ("last_activity", "upload_path", )

admin.site.register(AuroraUser, AuroraUserAdmin)