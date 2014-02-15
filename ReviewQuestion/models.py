from django.db import models


class ReviewQuestion(models.Model):
    challenge = models.ForeignKey('Challenge.Challenge')
    order = models.SmallIntegerField()
    text = models.TextField(null=True)
    boolean_answer = models.BooleanField(default=False)
    visible_to_author = models.BooleanField(default=True)

    def __unicode__(self):
        return str(self.text)