from django.db import models


class Challenge(models.Model):
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=100)
    prerequisite = models.ForeignKey('self', null=True)
    description = models.TextField()
    image_url = models.CharField(max_length=100)

    def get_previous(self):
        return self.prerequisite

    def get_next(self):  # TODO: this will not work if we branch out stacks
        next_challenge = Challenge.objects.filter(prerequisite=self)
        if len(next_challenge) > 0:
            return next_challenge[0]

