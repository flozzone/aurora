from django.db import models
from PortfolioUser.models import PortfolioUser


class Comment(models.Model):
    text = models.TextField
    author = models.ForeignKey(PortfolioUser)
    pub_date = models.DateTimeField('date published')
