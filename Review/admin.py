from django.contrib import admin

from Review.models import *


class ReviewAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None, {
                'fields': [
                    'elaboration',
                    'creation_time',
                    'submission_time',
                    'reviewer',
                ]
            }
        ),
    ]
    list_display = ('id', 'elaboration', 'creation_time', 'submission_time', 'reviewer', )
    search_fields = ('reviewer__username', 'elaboration__id',)
    readonly_fields = ("creation_time", )


admin.site.register(Review, ReviewAdmin)


class ReviewConfigAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None, {
                'fields': [
                    'candidate_offset_min',
                    'candidate_offset_max',
                ],
                'description': 'The offset is defined as passed time since the submission in hours.'
            }
        ),
    ]
    list_display = ('candidate_offset_min', 'candidate_offset_max', )


admin.site.register(ReviewConfig, ReviewConfigAdmin)


class ReviewEvaluationAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None, {
                'fields': [
                    'id',
                    'review',
                    'creation_time',
                    'user',
                    'appraisal',
                ]
            }
        ),
    ]

    def get_review_id(self, review_evaluation):
        url = '<a href="/admin/Review/review/{}/">{}</a>'
        review_id = review_evaluation.review.id
        return url.format(review_id, review_id)

    get_review_id.short_description = 'Review'
    get_review_id.allow_tags = True

    def get_review_author_id(self, review_evaluation):
        url = '<a href="/admin/AuroraUser/aurorauser/{}/">{}</a>'
        user_id = review_evaluation.review.reviewer.id
        return url.format(user_id, user_id)

    get_review_author_id.short_description = 'Review Author'
    get_review_author_id.allow_tags = True

    def get_review_challenge_name(self, review_evaluation):
        url = '<a href="/admin/Challenge/challenge/{}/">{}</a>'
        challenge_id = review_evaluation.review.elaboration.challenge.id
        challenge_title = review_evaluation.review.elaboration.challenge.title
        return url.format(challenge_id, challenge_title)

    get_review_challenge_name.short_description = 'Review Challenge'
    get_review_challenge_name.allow_tags = True

    list_display = (
        'id',
        'get_review_id',
        'get_review_author_id',
        'get_review_challenge_name',
        'creation_time',
        'user',
        'appraisal',
    )


admin.site.register(ReviewEvaluation, ReviewEvaluationAdmin)