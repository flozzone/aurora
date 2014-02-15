from django.contrib import admin
from Evaluation.models import *

class EvaluationAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None, {
                'fields': [
                    'submission',
                    'tutor',
                    'evaluation_text',
                    'evaluation_points',
                    'submission_time',
                    'lock_time',
                ]
            }
        ),
    ]
    list_display = ('id', 'submission', 'tutor', 'evaluation_text', 'evaluation_points', 'submission_time', 'lock_time', )

admin.site.register(Evaluation, EvaluationAdmin)