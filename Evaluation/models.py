from datetime import timedelta, datetime
from django.db import models


class Evaluation(models.Model):
    submission = models.ForeignKey('Elaboration.Elaboration')
    tutor = models.ForeignKey('AuroraUser.AuroraUser')
    creation_date = models.DateTimeField(auto_now_add=True)
    evaluation_text = models.TextField()
    evaluation_points = models.IntegerField(default=0)
    submission_time = models.DateTimeField(null=True)
    lock_time = models.DateTimeField(null=True)

    def is_older_15min(self):
        if not self.lock_time:
            return False
        if self.lock_time + timedelta(minutes=15) < datetime.now():
            return True
        return False