from django.contrib import admin
from Evaluation.models import *

class EvaluationAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None, {
                'fields': [
                    'submission',
                    'tutor',
                    'creation_date',
                    'evaluation_text',
                    'evaluation_points',
                    'submission_time',
                    'lock_time',
                ]
            }
        ),
    ]
    list_display = ('id', 'submission', 'tutor', 'creation_date', 'evaluation_text', 'evaluation_points', 'submission_time', 'lock_time', )
    readonly_fields = ("creation_date",)

admin.site.register(Evaluation, EvaluationAdmin)