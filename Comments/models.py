from django.db import models as models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
# from PortfolioUser.models import PortfolioUser


class Tag(models.Model):
    name = models.CharField(max_length=10)

    def __unicode__(self):
        return self.name


class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey('PortfolioUser.PortfolioUser')
    post_date = models.DateTimeField('date posted')
    parent = models.ForeignKey('self', null=True, related_name='children')
    score = models.IntegerField(default=0)
    visible = models.BooleanField(default=False)

    # Foreign object this Comment is attached to
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    PUBLIC = 'public'
    STAFF = 'staff'
    PRIVATE = 'private'
    VISIBILITY_CHOICES = (
        (PUBLIC, 'public'),
        (STAFF, 'staff only'),
        (PRIVATE, 'private')
    )

    visibility = models.CharField(max_length=10,
                                  choices=VISIBILITY_CHOICES,
                                  default=PUBLIC)

    custom_visibility = models.ManyToManyField('PortfolioUser.PortfolioUser', related_name='visible_comments_set')
    bookmarked_by = models.ManyToManyField('PortfolioUser.PortfolioUser', related_name='bookmarked_comments_set')
    was_voted_on_by = models.ManyToManyField('PortfolioUser.PortfolioUser', related_name='voted_comments_set')
    tags = models.ManyToManyField(Tag)

    def responses(self):
        return self.children.all().order_by('post_date')

    def __str__(self):
        return self.text[:20]

    def __unicode__(self):
        return self.text[:20]


class CommentReferenceObject(models.Model):
    """
    If there is no other Object available this Model can be used to create
    reference Objects. Comments can then be attached to that reference Object.
    """
    def __unicode__(self):
        return str(self.id)