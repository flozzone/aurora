from datetime import datetime, timedelta

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Count

from Comments.models import Comment
from Evaluation.models import Evaluation
from Review.models import Review
from FileUpload.models import UploadFile


class Elaboration(models.Model):
    challenge = models.ForeignKey('Challenge.Challenge')
    user = models.ForeignKey('PortfolioUser.PortfolioUser')
    creation_time = models.DateTimeField(auto_now_add=True)
    elaboration_text = models.TextField(null=True)
    submission_time = models.DateTimeField(null=True)

    def __unicode__(self):
        return str(self.id)

    def is_started(self):
        if self.elaboration_text:
            return True
        if UploadFile.objects.filter(elaboration=self).exists():
            return True
        return False

    def is_submitted(self):
        if self.submission_time:
            return True
        return False

    def is_evaluated(self):
        evaluation = self.get_evaluation()
        if evaluation:
            if evaluation.submission_time:
                return True
        return False

    def get_evaluation(self):
        evaluation = Evaluation.objects.filter(submission=self)
        if evaluation.exists():
            return evaluation[0]
        return None

    def is_reviewed_2times(self):
        if Review.objects.filter(elaboration=self, submission_time__isnull=False).count() < 2:
            return False
        return True

    def is_older_3days(self):
        if not self.is_submitted():
            return False
        if self.submission_time + timedelta(3) > datetime.now():
            return False
        return True

    def get_challenge_elaborations(self):
        elaborations = Elaboration.objects.filter(challenge=self.challenge, submission_time__isnull=False)
        if elaborations.exists():
            return elaborations
        return False

    def get_others(self):
        elaborations = []
        for elaboration in Elaboration.objects.filter(challenge=self.challenge, submission_time__isnull=False).exclude(pk=self.id):
            if not elaboration.user.is_staff:
                elaborations.append(elaboration)
        return elaborations

    @staticmethod
    def get_sel_challenge_elaborations(challenge):
        elaborations = Elaboration.objects.filter(challenge=challenge, submission_time__isnull=False)
        if elaborations.exists():
            return elaborations
        return False

    @staticmethod
    def get_missing_reviews():
        missing_reviews = []
        for elaboration in Elaboration.objects.all():
            if not elaboration.is_reviewed_2times() and elaboration.is_older_3days() \
                and not elaboration.challenge.is_final_challenge() and not elaboration.user.is_staff and elaboration.is_submitted():
                    missing_reviews.append(elaboration)
        return missing_reviews

    @staticmethod
    def get_top_level_challenges():
        top_level_challenges = []
        for elaboration in Elaboration.objects.all():
            if elaboration.challenge.is_final_challenge() and elaboration.is_submitted() \
                and not elaboration.is_evaluated() and not elaboration.user.is_staff:
                    top_level_challenges.append(elaboration)
        return top_level_challenges

    @staticmethod
    def get_non_adequate_work():
        non_adequate_work = []
        for review in Review.objects.filter(appraisal=Review.NOTHING):
            if not review.elaboration.is_evaluated() and review.elaboration.is_submitted():
                if not review.elaboration in non_adequate_work and not review.elaboration.user.is_staff:
                    non_adequate_work.append(review.elaboration)
        return non_adequate_work

    @staticmethod
    def get_evaluated_non_adequate_work():
        non_adequate_work = []
        for review in Review.objects.filter(appraisal=Review.NOTHING):
            final_challenge = review.elaboration.challenge.get_final_challenge()
            final_elaboration = final_challenge.get_elaboration(review.elaboration.user)
            if final_elaboration:
                if final_elaboration.is_evaluated():
                    if not review.elaboration in non_adequate_work and not review.elaboration.user.is_staff:
                        non_adequate_work.append(review.elaboration)
        return non_adequate_work

    @staticmethod
    def get_review_candidate(challenge, user):
        already_submitted_reviews_ids = (
            Review
            .objects.filter(reviewer=user, elaboration__challenge=challenge)
            .values_list('elaboration__id', flat=True)
        )
        candidates = (
            Elaboration
            .objects.filter(challenge=challenge, submission_time__isnull=False)
            .exclude(user=user)
            .exclude(user__is_staff=True)
            .annotate(num_reviews=Count('review'))
            .exclude(id__in=already_submitted_reviews_ids)
        ).order_by('num_reviews')

        if candidates.exists():
            return candidates[0]

        candidates = (
            Elaboration
            .objects.filter(challenge=challenge, submission_time__isnull=False)
            .exclude(user__is_staff=False)
            .annotate(num_reviews=Count('review'))
            .exclude(id__in=already_submitted_reviews_ids)
        ).order_by('num_reviews')

        if candidates.exists():
            return candidates[0]
        print("Error! No dummy elaborations created.")
        return None

    def get_success_reviews(self):
        return Review.objects.filter(elaboration=self, appraisal=Review.SUCCESS)

    def get_nothing_reviews(self):
        return Review.objects.filter(elaboration=self, appraisal=Review.NOTHING)

    def get_fail_reviews(self):
        return Review.objects.filter(elaboration=self, appraisal=Review.FAIL)

    def get_awesome_reviews(self):
        return Review.objects.filter(elaboration=self, appraisal=Review.AWESOME)

    def is_passing_peer_review(self):
        nothing_reviews = Review.objects.filter(elaboration=self, appraisal=Review.NOTHING)
        return not nothing_reviews

    @staticmethod
    def get_complaints(context):
        elaborations = []
        for review in Review.objects.all():
            if Comment.query_comments_without_responses(review, context['user']):
                if not review.elaboration in elaborations:
                    elaborations.append(review.elaboration)
        return elaborations

    @staticmethod
    def get_awesome():
        awesome = []
        for review in Review.objects.filter(appraisal=Review.AWESOME, submission_time__isnull=False):
            if not review.elaboration in awesome and not review.elaboration.user.is_staff:
                awesome.append(review.elaboration)
        return awesome

    @staticmethod
    def get_stack_elaborations(stack):
        elaborations = []
        for challenge in stack.get_challenges():
            for elaboration in challenge.get_elaborations():
                elaborations.append(elaboration)
        return elaborations

    @staticmethod
    def get_course_elaborations(course):
        elaborations = []
        for challenge in course.get_course_challenges():
            for elaboration in challenge.get_elaborations():
                elaborations.append(elaboration)
        return elaborations

    def get_visible_comments(self):
        comments = []
        for review in Review.objects.filter(elaboration=self.id):
            for comment in Comment.objects.filter(visibility=Comment.PUBLIC,
                                                  content_type=ContentType.objects.get_for_model(Review),
                                                  object_id=review.id):
                comments.append(comment)
        for elaboration in Elaboration.objects.filter(id=self.id):
            for comment in Comment.objects.filter(visibility=Comment.PUBLIC,
                                                  content_type=ContentType.objects.get_for_model(Elaboration),
                                                  object_id=elaboration.id):
                comments.append(comment)
        return comments

    def get_invisible_comments(self):
        comments = []
        for review in Review.objects.filter(elaboration=self.id):
            for comment in Comment.objects.filter(visibility=Comment.STAFF,
                                                  content_type=ContentType.objects.get_for_model(Review),
                                                  object_id=review.id):
                comments.append(comment)
        for elaboration in Elaboration.objects.filter(id=self.id):
            for comment in Comment.objects.filter(visibility=Comment.STAFF,
                                                  content_type=ContentType.objects.get_for_model(Elaboration),
                                                  object_id=elaboration.id):
                comments.append(comment)
        return comments