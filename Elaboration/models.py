from django.db import models
from datetime import datetime, timedelta
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
        if Evaluation.objects.filter(submission=self, user=self.user):
            return Evaluation.objects.filter(submission=self, user=self.user).order_by('id')[0]
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

    @staticmethod
    def get_missing_reviews():
        missing_reviews = []
        for elaboration in Elaboration.objects.all():
            if not elaboration.is_reviewed_3times() and elaboration.is_older_3days():
                missing_reviews.append(elaboration)
        return missing_reviews