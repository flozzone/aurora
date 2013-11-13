from django.db import models


class ReviewQuestion(models.Model):
    challenge = models.ForeignKey('Challenge.Challenge')
    order = models.SmallIntegerField(unique=True)
    text = models.TextField(null=True)
    boolean_answer = models.BooleanField(default=False)
    answer_visible_to_student = models.BooleanField(default=True)
