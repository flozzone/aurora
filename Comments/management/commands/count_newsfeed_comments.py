from django.core.management.base import NoArgsCommand
from Comments.models import Comment
from Comments.models import CommentReferenceObject
from django.contrib.contenttypes.models import ContentType

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        ref_object = CommentReferenceObject.objects.get(name='newsfeed');
        content_type = ContentType.objects.get_for_model(ref_object)
        ref_id = ref_object.id
        ref_type = content_type.id

        newsfeed_parents = Comment.objects.filter(parent=None, content_type__pk=ref_type, object_id=ref_id, visibility=Comment.PUBLIC)

        parent_counts = {}
        for c in newsfeed_parents:
          if not c.author in parent_counts.keys():
            parent_counts[c.author] = 0
          parent_counts[c.author] += 1

        newsfeed_all = Comment.objects.filter(content_type__pk=ref_type, object_id=ref_id, visibility=Comment.PUBLIC)
        newsfeed_replies = list(set(newsfeed_all) - set(newsfeed_parents))

        reply_counts = {}
        for c in newsfeed_replies:
          if not c.author in reply_counts.keys():
            reply_counts[c.author] = 0
          reply_counts[c.author] += 1

        print('nickname user(matrnr)    no_parents  no_replies')
        authors = set(list(parent_counts.keys()) + list(reply_counts.keys()))
        for user in authors:
          parent_count = parent_counts[user] if user in parent_counts.keys() else 0
          reply_count = reply_counts[user] if user in reply_counts.keys() else 0
          print(str(user.nickname) + "	" + str(user) + "	" + str(parent_count) + "	" + str(reply_count))
