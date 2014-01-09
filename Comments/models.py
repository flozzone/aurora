from django.db import models as models
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic


class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey('PortfolioUser.PortfolioUser')
    post_date = models.DateTimeField('date posted')
    parent = models.ForeignKey('self', null=True, related_name='children')
    visible = models.BooleanField(default=False)

    # Foreign object this Comment is attached to
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def responses(self):
        return self.children.all().order_by('-post_date')

    def __unicode__(self):
        return self.text[:20]


class CommentReferenceObject(models.Model):
    """
    If there is no other Object available this Model can be used to create
    reference Objects. Comments can then be attached to that reference Object.
    """
    def __unicode__(self):
        return str(self.id)