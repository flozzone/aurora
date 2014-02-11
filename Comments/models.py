from django.db import models as models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db.models import Q


class Tag(models.Model):
    name = models.CharField(max_length=10)

    def __unicode__(self):
        return self.name


class CommentListRevision(models.Model):
    number = models.BigIntegerField(default=0)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = ('content_type', 'object_id')

    @staticmethod
    def get_or_create(ref_object):
        ref_type = ContentType.objects.get_for_model(ref_object)

        try:
            revision = CommentListRevision.objects.get(
                content_type__pk=ref_type.id,
                object_id=ref_object.id)
        except CommentListRevision.DoesNotExist:
            revision = CommentListRevision.objects.create(content_object=ref_object)

        return revision

    @staticmethod
    def get_by_ref_numbers(ref_id, ref_type):
        return CommentListRevision.objects.get(
            content_type__pk=ref_type,
            object_id=ref_id)

    @staticmethod
    def get_by_comment(comment):
        return CommentListRevision.get_by_ref_numbers(comment.object_id, comment.content_type.id)

    def increment(self):
        self.number += 1
        self.save()


class Vote(models.Model):
    UP = True
    DOWN = False
    direction = models.BooleanField(choices=((UP, True), (DOWN, False)),
                                    default=True)

    voter = models.ForeignKey('PortfolioUser.PortfolioUser')
    comment = models.ForeignKey('Comment', related_name='votes')

    class Meta:
        unique_together = ('voter', 'comment')


class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey('PortfolioUser.PortfolioUser')
    post_date = models.DateTimeField('date posted')
    delete_date = models.DateTimeField('date posted', null=True)
    deleter = models.ForeignKey('PortfolioUser.PortfolioUser', related_name='deleted_comments_set', null=True)
    parent = models.ForeignKey('self', null=True, related_name='children')
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
        (PRIVATE, 'private note')
    )

    visibility = models.CharField(max_length=10,
                                  choices=VISIBILITY_CHOICES,
                                  default=PUBLIC)

    bookmarked_by = models.ManyToManyField('PortfolioUser.PortfolioUser', related_name='bookmarked_comments_set')
    tags = models.ManyToManyField(Tag)

    @property
    def score(self):
        up_votes = self.votes.filter(direction=Vote.UP).count()
        down_votes = self.votes.filter(direction=Vote.DOWN).count()
        return up_votes - down_votes

    def responses(self):
        responses = self.children.order_by('post_date')
        responses = Comment.filter_visible(responses, self.requester)
        Comment.set_flags(responses, self.requester)
        return responses

    def add_up_vote(self, voter):
        vote = Vote.objects.create(direction=Vote.UP, voter=voter, comment=self)

    def add_down_vote(self, voter):
        vote = Vote.objects.create(direction=Vote.DOWN, voter=voter, comment=self)

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
        visible = visible.order_by('-post_date')

        # Only when all query actions are done we can set custom properties to
        # the objects in the queryset. If another query method is called (even if
        # it's just order_by() the Instances and their custom non persistent properties
        # will be overwritten.

        # Comment.set_permission_flags(visible, requester)
        Comment.set_flags(visible, requester)
        return visible

    @staticmethod
    def query_all(ref_object_id, ref_type_id, requester):
        queryset = Comment.objects.filter(
            content_type__pk=ref_type_id,
            object_id=ref_object_id)

        visible_comments = Comment.filter_visible(queryset, requester)
        # Comment.set_permission_flags(visible_comments, requester)
        Comment.set_flags(visible_comments, requester)
        return visible_comments

    @staticmethod
    def query_bookmarks(requester):
        result = requester.bookmarked_comments_set.all().order_by('-post_date')
        Comment.filter_visible(result, requester)
        Comment.set_flags(result, requester)
        return result

    # @staticmethod
    # def set_bookmark_flags(comment_set, requester):
    #     for comment in comment_set:
    #         comment.bookmarked = True if comment.bookmarked_by.filter(pk=requester.id).exists() else False
    #         comment.requester = requester

    @staticmethod
    def set_flags(comment_set, requester):
        for comment in comment_set:
            comment.requester = requester
            # comment.set_visibility_flag(requester)
            comment.bookmarked = True if comment.bookmarked_by.filter(pk=requester.id).exists() else False

    def set_visibility_flag(self, requester):
        self.visible = False
        if self.visibility == Comment.PUBLIC:
            self.visible = True
            return

        if self.author == requester:
            self.visible = True
            return

        if self.visibility == Comment.STAFF and requester.is_staff:
            self.visibility = True
            return

        if self.parent.author == requester:
            self.visibility = True
            return

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
            if comment.children.all().filter(deleter=None).count() <= 0:
                # remove parent from queryset
                comment_set = comment_set.exclude(id=comment.id)

        return comment_set

    @staticmethod
    def filter_visible(queryset, requester):
        non_private_or_authored = queryset.filter(~Q(visibility=Comment.PRIVATE) | Q(author=requester))
        if requester.is_staff:
            return non_private_or_authored

        return non_private_or_authored.filter(
            ~Q(visibility=Comment.STAFF) | Q(author=requester) | Q(parent__author=requester))


class CommentsConfig(models.Model):
    key = models.CharField(primary_key=True, max_length=30)
    value = models.CharField(max_length=20)

    factor = 1000

    @staticmethod
    def setup():
        CommentsConfig.objects.create(key='polling_active',
                                      value='5')
        CommentsConfig.objects.create(key='polling_idle',
                                      value='60')

    @staticmethod
    def get_polling_interval():
        active = CommentsConfig.objects.get(key='polling_active')
        idle = CommentsConfig.objects.get(key='polling_idle')

        return int(active.value) * CommentsConfig.factor, int(idle.value) * CommentsConfig.factor

    def __unicode__(self):
        return self.key

    def __str__(self):
        return self.key


class CommentReferenceObject(models.Model):
    """
    If there is no other Object available this Model can be used to create
    reference Objects. Comments can then be attached to that reference Object.
    """
    def __unicode__(self):
        return str(self.id)