from django.db import models as models
from django.utils import timezone
from PortfolioUser.models import PortfolioUser


class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(PortfolioUser)
    post_date = models.DateTimeField('date posted')
    parent = models.ForeignKey('self', null=True, related_name='children')
    # TODO ForeignKey hinzufuegen, der auf das Objekt zeigt, zu denen der Comment gehoert

    @property
    def responses(self):
        return self.children.all().order_by('-post_date')

    def __unicode__(self):
        return self.text[:20]
