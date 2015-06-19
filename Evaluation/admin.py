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
    list_display = ('id', 'get_submission_author', 'get_submission', 'get_tutor', 'creation_date', 'evaluation_text', 'evaluation_points', 'submission_time', 'lock_time', )
    readonly_fields = ("creation_date",)

    def get_submission(self, evaluation):
        url = '<a href="/admin/Elaboration/elaboration/{}/">{}</a>'
        elaboration_id = evaluation.submission.id
        return url.format(elaboration_id, elaboration_id)
    get_submission.short_description = 'Submission'
    get_submission.allow_tags = True

    def get_submission_author(self, evaluation):
        url = '<a href="/admin/AuroraUser/aurorauser/{}/">{}</a>'
        user_id = evaluation.submission.user.id
        matriculation_number = evaluation.submission.user.matriculation_number
        return url.format(user_id, matriculation_number)
    get_submission_author.short_description = 'Submission author'
    get_submission_author.allow_tags = True

    def get_tutor(self, evaluation):
        url = '<a href="/admin/AuroraUser/aurorauser/{}/">{}</a>'
        user_id = evaluation.tutor.id
        nickname = evaluation.tutor.nickname
        return url.format(user_id, nickname)
    get_tutor.short_description = 'Tutor'
    get_tutor.allow_tags = True

    search_fields = ['tutor__nickname']

admin.site.register(Evaluation, EvaluationAdmin)