from django.db import models


class Evaluation(models.Model):
    submission = models.ForeignKey('Elaboration.Elaboration')
    user = models.ForeignKey('PortfolioUser.PortfolioUser')
    creation_date = models.DateTimeField(auto_now_add=True)
    evaluation_text = models.TextField()
    evaluation_points = models.IntegerField(null=True)
    submission_time = models.DateTimeField(null=True)