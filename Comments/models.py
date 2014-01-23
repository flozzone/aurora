from django.db import models as models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db.models import Q


class Tag(models.Model):
    name = models.CharField(max_length=10)

    def __unicode__(self):
        return self.name


class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey('PortfolioUser.PortfolioUser')
    post_date = models.DateTimeField('date posted')
    delete_date = models.DateTimeField('date posted', null=True)
    deleter = models.ForeignKey('PortfolioUser.PortfolioUser', related_name='deleted_comments_set', null=True)
    parent = models.ForeignKey('self', null=True, related_name='children')
    score = models.IntegerField(default=0)
    promoted = models.BooleanField(default=False)

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

    # custom_visibility = models.ManyToManyField('PortfolioUser.PortfolioUser', related_name='visible_comments_set')
    bookmarked_by = models.ManyToManyField('PortfolioUser.PortfolioUser', related_name='bookmarked_comments_set')
    was_voted_on_by = models.ManyToManyField('PortfolioUser.PortfolioUser', related_name='voted_comments_set')
    tags = models.ManyToManyField(Tag)

    def responses(self):
        return self.children.all().order_by('post_date')

    def __str__(self):
        return str(self.id) + ": " + self.text[:30]

    def __unicode__(self):
        return str(self.id) + ": " + self.text[:30]

    @staticmethod
    def query_top_level_sorted(ref_object_id, ref_type_id, requester):
        queryset_all = Comment.objects.filter(
            parent=None,
            content_type__pk=ref_type_id,
            object_id=ref_object_id)

        visible = Comment.filter_visible(queryset_all, requester)
        visible = Comment.filter_deleted(visible)
        # Comment.set_permission_flags(visible, requester)
        return visible.order_by('-post_date')

    @staticmethod
    def query_all(ref_object_id, ref_type_id, requester):
        queryset = Comment.objects.filter(
            content_type__pk=ref_type_id,
            object_id=ref_object_id)

        visible_comments = Comment.filter_visible(queryset, requester)
        # Comment.set_permission_flags(visible_comments, requester)
        return visible_comments

    # TODO not working for some weird reason
    # TODO delete or fix
    @staticmethod
    def set_permission_flags(comment_set, requester):
        for comment in comment_set:
            if comment.author == requester or requester.is_staff:
                comment.editable = True
                comment.deletable = True

            if comment.deleter is not None:
                comment.deletable = False

    @staticmethod
    def filter_deleted(comment_set):
        # for every deleted parent
        for comment in comment_set.exclude(deleter=None):
            # if not deleted responses <= 0
            if comment.responses().filter(deleter=None).count() <= 0:
                # remove parent from queryset
                comment_set = comment_set.exclude(id=comment.id)

        return comment_set

    @staticmethod
    def filter_visible(queryset, requester):
        non_private_or_authored = queryset.filter(~Q(visibility=Comment.PRIVATE) | Q(author=requester))
        if requester.is_staff:
            return non_private_or_authored

        return non_private_or_authored.exclude(visibility=Comment.STAFF)


class CommentsRuntimeConfig:
    polling_interval = 5000


class CommentReferenceObject(models.Model):
    """
    If there is no other Object available this Model can be used to create
    reference Objects. Comments can then be attached to that reference Object.
    """
    def __unicode__(self):
        return str(self.id)