from django.contrib import admin
from PortfolioUser.models import *

class PortfolioUserAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None, {
                'fields': [
                    'nickname',
                    'last_activity',
                    'statement',
                    'upload_path',
                    'avatar',
                    'matriculation_number',
                    'study_code',
                    'last_selected_course',
                ]
            }
        ),
    ]
    list_display = ('id', 'nickname', 'last_activity', 'statement', 'upload_path', 'avatar', 'matriculation_number', 'study_code', 'last_selected_course', )
    readonly_fields = ("last_activity", "upload_path", )

admin.site.register(PortfolioUser, PortfolioUserAdmin)