from django.db import models

# Create your models here.

class Challenge(models.Model):
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=100)
    prerequisite = models.ForeignKey('self', null=True)
    description = models.TextField()
    cardImageUrl = models.CharField('card url', max_length=100)
    backgroundImageUrl = models.CharField('background url', max_length=100)

    def getParent(self):
        return self.prerequisite

    def getChild(self):
        return Challenge.objects.filter(challenge=self.prerequisite)
