from django.db import models
from django.utils import timezone
from PortfolioUser.models import PortfolioUser


class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(PortfolioUser)
    post_date = models.DateTimeField('date posted')

    @property
    def post_date_relative(self):
        timedelta = timezone.now() - self.post_date

        # TODO beautify with babel: http://stackoverflow.com/questions/410221/natural-relative-days-in-python
        if timedelta.days > 6:
            weeks = timedelta.days/7
            return str(weeks) + " weeks ago" if weeks > 1 else "a week ago"

        days = timedelta.days
        if days > 0:
            return str(days) + " days ago" if days > 1 else "a day ago"

        hours = timedelta.seconds/3600
        if hours > 0:
            return str(hours) + " hours ago" if hours > 1 else "an hour ago"

        minutes = timedelta.seconds/60
        if minutes > 0:
            return str(minutes) + " minutes ago" if minutes > 1 else "a minute ago"

        return "just a moment ago"

    def __unicode__(self):
        return self.text[:20]
