from django.db import models

# Create your models here.

class Evaluation(models.Model):
    submission = models.ForeignKey('Submission.Submission')
    user = models.ForeignKey('PortfolioUser.PortfolioUser')
    creationDate = models.DateTimeField(auto_now_add=True)
    evaluationState = models.CharField(max_length=100)