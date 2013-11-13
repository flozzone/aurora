from django.db import models


class ReviewAnswer(models.Model):
    peer_review_question = models.ForeignKey('ReviewQuestion.ReviewQuestion')
    text = models.TextField(null=True)
    creation_time = models.DateTimeField(auto_now_add=True)
