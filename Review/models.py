from django.db import models


class Review(models.Model):
    elaboration = models.ForeignKey('Elaboration.Elaboration')
    creation_time = models.DateTimeField(auto_now_add=True)
    reviewer = models.ForeignKey('PortfolioUser.PortfolioUser')
    NOTHING = 'N'
    FAIL = 'F'
    SUCCESS = 'S'
    APPRAISAL_CHOICES = (
        (NOTHING, 'Not even trying'),
        (FAIL, 'Fail'),
        (SUCCESS, 'Success'),
    )
    appraisal = models.CharField(max_length=1,
                                 choices=APPRAISAL_CHOICES,
                                 default=NOTHING)
    awesome = models.BooleanField(default=False)