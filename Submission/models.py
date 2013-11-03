from django.db import models

# Create your models here.

class Submission(models.Model):
    elaboration = models.ForeignKey('Elaboration.Elaboration')
    submission_date = models.DateTimeField(auto_now_add=True)