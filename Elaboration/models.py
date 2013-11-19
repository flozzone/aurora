from django.db import models
from datetime import datetime, timedelta

class Elaboration(models.Model):
    challenge = models.ForeignKey('Challenge.Challenge')
    user = models.ForeignKey('PortfolioUser.PortfolioUser')
    creation_time = models.DateTimeField(auto_now_add=True)
    elaboration_text = models.TextField(null=True)
    submission_time = models.DateTimeField(null=True)

    def is_waiting_elaboration(self):
        if self.challenge.is_final_challenge():
            return False
        # sumbission needs to be at least 3 days old
        return True if self.submission_time + timedelta(3) < datetime.now() else False

    @staticmethod
    def get_waiting_elaborations():
        waiting_elaborations = []
        for elaboration in Elaboration.objects.all():
            if elaboration.is_waiting_elaboration():
                waiting_elaborations.append(elaboration)
        return waiting_elaborations

    def is_submitted(self):
        if self.submission_time:
            return True
        else:
            return False
