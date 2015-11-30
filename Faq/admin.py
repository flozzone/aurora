from django.contrib import admin
from Faq.models import Faq


class FaqAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None, {
                'fields': [
                    'course',
                    'question',
                    'answer',
                ]
            }
        ),
    ]
    list_display = (
        'question',
        'answer',
    )

admin.site.register(Faq, FaqAdmin)