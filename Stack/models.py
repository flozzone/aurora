from django.db import models

# Create your models here.

class Stack(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    course = models.ForeignKey('Course.Course')

class StackChallengeRelation(models.Model):
    stack = models.ForeignKey('Stack.Stack')
    challenge = models.ForeignKey('Challenge.Challenge')