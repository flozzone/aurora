from django.db import models
from django.utils import timezone
from PortfolioUser.models import PortfolioUser


class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(PortfolioUser)
    post_date = models.DateTimeField('date posted')

    @property
    def post_date_relative(self):
        post_date_rel = timezone.timedelta(self.post_date - timezone.now())
        return post_date_rel

    def __unicode__(self):
        return self.text[:20]
