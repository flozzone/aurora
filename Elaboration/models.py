from datetime import datetime, timedelta
from django.contrib.contenttypes.models import ContentType
from django.db import models
from Comments.models import Comment
from Evaluation.models import Evaluation
from Review.models import Review

class Elaboration(models.Model):
    challenge = models.ForeignKey('Challenge.Challenge')
    user = models.ForeignKey('PortfolioUser.PortfolioUser')
    creation_time = models.DateTimeField(auto_now_add=True)
    elaboration_text = models.TextField(null=True)
    submission_time = models.DateTimeField(null=True)

    def is_submitted(self):
        if self.submission_time:
            return True
        return False

    def get_evaluation(self):
        if Evaluation.objects.get(submission=self):
            return Evaluation.objects.get(submission=self)
        return False

    def is_reviewed_3times(self):
        if Review.objects.filter(elaboration=self).count() < 3:
            return False
        return True

    def is_older_3days(self):
        if not self.is_submitted():
            return False
        if self.submission_time + timedelta(3) < datetime.now():
            return False
        return True

    def get_challenge_elaborations(self):
        if Elaboration.objects.filter(challenge=self.challenge, submission_time__isnull=False):
            return Elaboration.objects.filter(challenge=self.challenge, submission_time__isnull=False)
        return False

    def get_others(self):
        if Elaboration.objects.filter(challenge=self.challenge, submission_time__isnull=False).exclude(pk=self.id):
            return Elaboration.objects.filter(challenge=self.challenge, submission_time__isnull=False).exclude(pk=self.id)
        return False

    @staticmethod
    def get_sel_challenge_elaborations(challenge):
        if Elaboration.objects.filter(challenge=challenge, submission_time__isnull=False):
            return Elaboration.objects.filter(challenge=challenge, submission_time__isnull=False)
        return False

    @staticmethod
    def get_missing_reviews():
        missing_reviews = []
        for elaboration in Elaboration.objects.all():
            if not elaboration.is_reviewed_3times() and elaboration.is_older_3days() and not elaboration.challenge.is_final_challenge():
                missing_reviews.append(elaboration)
        return missing_reviews

    @staticmethod
    def get_top_level_challenges():
        top_level_challenges = []
        for elaboration in Elaboration.objects.all():
            if elaboration.challenge.is_final_challenge():
                top_level_challenges.append(elaboration)
        return top_level_challenges

    @staticmethod
    def get_non_adequate_work():
        non_adequate_work = []
        for review in Review.objects.filter(appraisal=Review.FAIL):
            non_adequate_work.append(review.elaboration)
        return non_adequate_work

    @staticmethod
    def get_review_candidate(challenge, user):
        candidates = Elaboration.objects.filter(challenge=challenge).exclude(user=user)
        if candidates:
            best_candidate = None
        else:
            return None
        for candidate in candidates:
            if not Review.objects.filter(elaboration=candidate, reviewer=user):
                if best_candidate:
                    if Review.get_review_amount(candidate) < Review.get_review_amount(best_candidate):
                        best_candidate = candidate
                else:
                    best_candidate = candidate
        return best_candidate

    def get_success_reviews(self):
        return Review.objects.filter(elaboration=self, appraisal=Review.SUCCESS)

    def get_nothing_reviews(self):
        return Review.objects.filter(elaboration=self, appraisal=Review.NOTHING)

    def get_fail_reviews(self):
        return Review.objects.filter(elaboration=self, appraisal=Review.FAIL)

    def get_awesome_reviews(self):
        return Review.objects.filter(elaboration=self, appraisal=Review.AWESOME)

    @staticmethod
    def get_non_adequate_reviews():
        elaborations = []
        # for review in Review.objects.filter(escalate=True):
        #     elaborations.append(review.elaboration)
        return elaborations

    @staticmethod
    def get_awesome():
        awesome = []
        for review in Review.objects.filter(appraisal=Review.AWESOME):
            awesome.append(review.elaboration)
        return awesome

    @staticmethod
    def get_stack_elaborations(stack):
        elaborations = []
        for challenge in stack.get_challenges():
            for elaboration in challenge.get_submissions():
                elaborations.append(elaboration)
        return elaborations

    @staticmethod
    def get_course_elaborations(course):
        elaborations = []
        for challenge in course.get_course_challenges():
            for elaboration in challenge.get_submissions():
                elaborations.append(elaboration)
        return elaborations

    def get_visible_comments(self):
        return Comment.objects.filter(visible=True, content_type=ContentType.objects.get_for_model(Elaboration), object_id=self.id)

    def get_invisible_comments(self):
        return Comment.objects.filter(visible=False, content_type=ContentType.objects.get_for_model(Elaboration), object_id=self.id)