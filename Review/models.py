from django.db import models
from taggit.managers import TaggableManager
from django.contrib.contenttypes.models import ContentType

class Review(models.Model):
    elaboration = models.ForeignKey('Elaboration.Elaboration')
    creation_time = models.DateTimeField(auto_now_add=True)
    submission_time = models.DateTimeField(null=True)
    reviewer = models.ForeignKey('AuroraUser.AuroraUser')
    tags = TaggableManager()

    NOTHING = 'N'
    FAIL = 'F'
    SUCCESS = 'S'
    AWESOME = 'A'
    APPRAISAL_CHOICES = (
        (NOTHING, 'Not even trying'),
        (FAIL, 'Fail'),
        (SUCCESS, 'Success'),
        (AWESOME, 'Awesome'),
    )
    appraisal = models.CharField(max_length=1, choices=APPRAISAL_CHOICES, null=True)

    def __unicode__(self):
        return str(self.id)

    def get_content_type_id(self):
        return ContentType.objects.get_for_model(self).id

    def add_tags_from_text(self, text):
        tags = text.split(',');
        tags = [tag.lower().strip() for tag in tags]
        self.tags.add(*tags)

    def remove_tag(self, tag):
        self.tags.remove(tag)

    @staticmethod
    def get_open_review(challenge, user):
        open_reviews = Review.objects.filter(elaboration__challenge=challenge, submission_time__isnull=True,
                                             reviewer=user)
        if open_reviews:
            return open_reviews[0]
        else:
            return None


class ReviewEvaluation(models.Model):
    review = models.ForeignKey('Review.Review')
    creation_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey('AuroraUser.AuroraUser')

    DEFAULT = 'D'
    NEGATIVE = 'N'
    POSITIVE = 'P'
    APPRAISAL_CHOICES = (
        (DEFAULT, 'Average Review'),
        (NEGATIVE, 'Flag this review as meaningless or offensive'),
        (POSITIVE, 'This review was helpful'),
    )
    appraisal = models.CharField(max_length=1, choices=APPRAISAL_CHOICES, default='D')

    @staticmethod
    def get_default_review_evaluations(user, course):
        return ReviewEvaluation.objects.filter(review__reviewer=user, review__elaboration__challenge__course=course,
                                               appraisal=ReviewEvaluation.DEFAULT).count()

    @staticmethod
    def get_positive_review_evaluations(user, course):
        return ReviewEvaluation.objects.filter(review__reviewer=user, review__elaboration__challenge__course=course,
                                               appraisal=ReviewEvaluation.POSITIVE).count()

    @staticmethod
    def get_negative_review_evaluations(user, course):
        return ReviewEvaluation.objects.filter(review__reviewer=user, review__elaboration__challenge__course=course,
                                               appraisal=ReviewEvaluation.NEGATIVE).count()
    @staticmethod
    def get_review_evaluation_percent(user, course):
        number_of_reviews = Review.objects.filter(elaboration__user=user, elaboration__challenge__course=course).count()
        number_of_review_evaluations = ReviewEvaluation.objects.filter(user=user, review__elaboration__challenge__course=course).count()
        if number_of_reviews == 0:
            return 0
        else:
            return number_of_review_evaluations/number_of_reviews

class ReviewConfig(models.Model):
    # in hours
    candidate_offset_min = models.IntegerField(default=0)
    candidate_offset_max = models.IntegerField(default=0)

    @staticmethod
    def get_candidate_offset_min():
        config = ReviewConfig.objects.all()
        if config.count() == 0:
            return 0
        else:
            return config[0].candidate_offset_min

    @staticmethod
    def get_candidate_offset_max():
        config = ReviewConfig.objects.all()
        if config.count() == 0:
            return 0
        else:
            return config[0].candidate_offset_max
