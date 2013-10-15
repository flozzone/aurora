from django.db import models

# Create your models here.

class Submission(models.Model):
    elaboration = models.ForeignKey('Elaboration.Elaboration')
    submissionDate = models.DateTimeField(auto_now_add=True)
    submissionState = models.CharField(max_length=100)