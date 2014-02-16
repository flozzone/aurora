from django.contrib import admin
from PortfolioUser.models import *

class PortfolioUserAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None, {
                'fields': [
                    'nickname',
                    'statement',
                    'avatar',
                    'matriculation_number',
                    'study_code',
                    'last_selected_course',
                ]
            }
        ),
    ]
    list_display = ('id', 'nickname', 'statement', 'avatar', 'matriculation_number', 'study_code', 'last_selected_course', )

admin.site.register(PortfolioUser, PortfolioUserAdmin)