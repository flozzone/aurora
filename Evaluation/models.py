from django.db import models


class Evaluation(models.Model):
    submission = models.ForeignKey('Elaboration.Elaboration')
    user = models.ForeignKey('PortfolioUser.PortfolioUser')
    creation_date = models.DateTimeField(auto_now_add=True)