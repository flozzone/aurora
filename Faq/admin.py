from django.contrib import admin
from Faq.models import Faq

from suit.admin import SortableModelAdmin


class FaqAdmin(SortableModelAdmin):
    fieldsets = [
        (
            None, {
                'fields': [
                    'course',
                    'question',
                    'answer'
                ]
            }
        ),
    ]
    list_display = (
        'question',
        'answer',
    )
    sortable = 'order'

admin.site.register(Faq, FaqAdmin)