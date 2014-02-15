from django.contrib import admin
from Stack.models import *

class StackAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None, {
                'fields': [
                    'title',
                    'description',
                    'course',
                ]
            }
        ),
    ]
    list_display = ('id', 'title', 'description', 'course', )

admin.site.register(Stack, StackAdmin)