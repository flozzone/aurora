from django.test import TestCase
from Comments.models import Comment, CommentReferenceObject
from PortfolioUser.models import PortfolioUser
from django.utils import timezone
from django.template import Context, Template
from django import template


def create_comment(text, author, reference_object, parent=None, days=0, minutes=0, seconds=0):
    """
    creates and returns a new Comment Model object that is not being persisted
    with text by author attached to reference_object

    Parameters
    ----------
    text: string
        Comment text
    author: PortfolioUser
        author of the Comment
    reference_object: django.db.models.Model
        the object the Comment should be attached to
    parent: Comments.models.Comment
        parent Comment i.e. the Comment the created Comment is responding to
    days, minutes, seconds: int
        time ago this Comment has been posted
    """
    delta = timezone.timedelta(days=-days, seconds=-(minutes*60) + seconds)
    post_date = timezone.now() + delta
    comment = Comment.objects.create(text=text, author=author, parent=parent, post_date=post_date,
                                     content_object=reference_object)
    return comment


def dummy_user_generator():
    i = 0
    while True:
        i += 1
        n = str(i)
        user = PortfolioUser(username='du'+n, first_name='first'+n,
                             last_name='last'+n, email='du'+n+'@foo.bar')
        user.nickname = 'duni' + n
        user.password = 'dupa' + n

        yield user


def dummy_comment_generator():
    # TODO implement
    pass

# class CommentMethodTests(TestCase):
#     user_generator = dummy_user_generator()
#
#     def test_post_date_relative_days_ago(self):
#         u = self.user_generator.next()
#         u.save()
#         c = create_comment("helo und so", u, days=2, minutes=8)
#         c.save()
#         self.assertEqual(c.post_date_relative, "2 days ago")


class ModelMethodTests(TestCase):
    def setUp(self):
        user_generator = dummy_user_generator()
        self.u1 = next(user_generator)
        self.u1.save()
        self.u2 = next(user_generator)
        self.u2.save()
        self.u3 = next(user_generator)
        self.u3.save()

        self.ref_object = CommentReferenceObject.objects.create()

        # self.comment = Comment.objects.create(text='inTests', parent=None, author=self.u1, post_date=timezone.now(),
                                              # content_object=self.ref_object)
        self.t1 = "text1"
        self.c1 = create_comment(self.t1, self.u1, self.ref_object)
        self.rt1 = "response text1"
        self.r1 = create_comment(self.rt1, self.u2, self.ref_object, parent=self.c1)
        self.t2 = "text2"
        self.c2 = create_comment(self.t2, self.u2, self.ref_object)
        self.t3 = "text3"
        self.c3 = create_comment(self.t3, self.u2, self.ref_object)
        self.rt2 = "response text2"
        self.r2 = create_comment(self.rt1, self.u1, self.ref_object, parent=self.c3)
        self.rt3 = "response text3"
        self.r3 = create_comment(self.rt1, self.u3, self.ref_object, parent=self.c3)
        self.t4 = "text4"
        self.c4 = create_comment(self.t4, self.u3, self.ref_object)

    def test_query_comments_without_responses(self):
        queryset = Comment.query_comments_without_responses(self.ref_object, self.u2)
        self.assertTrue(list(queryset) == [self.c4, self.c2])


class TagTests(TestCase):
    def setUp(self):
        user_generator = dummy_user_generator()
        self.u1 = next(user_generator)
        self.u1.save()
        self.u2 = next(user_generator)
        self.u2.save()
        self.u3 = next(user_generator)
        self.u3.save()

    # @staticmethod
    # def call_render(temp, context):
    #     t = Template('{% load comments %}' + temp)
    #     c = Context(context)
    #     return t.render(c)
    #
    # def no_test_render_comment_list_tag_without_parameter(self):
    #     temp = "{% render_comment_list for %}"
    #     context = {}
    #     with self.assertRaises(template.TemplateSyntaxError):
    #         self.call_render(temp, context)
    #
    # def no_test_render_comment_list_tag_without_for(self):
    #     temp = "{% render_comment_list is bar %}"
    #     context = {}
    #     with self.assertRaises(template.TemplateSyntaxError):
    #         self.call_render(temp, context)
    #
    # def test_render_comment_list_as_feed(self):
    #     ref_object = CommentReferenceObject()
    #     ref_object.save()
    #     text_c1 = "telephone booth is magic"
    #     c1 = create_comment(text_c1, self.u1, ref_object, days=5)
    #     c1.save()
    #     text_a1 = "yeah, i can even see the star dust"
    #     a1 = create_comment(text_a1, self.u2, ref_object, parent=c1, days=2)
    #     a1.save()
    #     text_a2 = "i am also like this huge fan of phone booths"
    #     a2 = create_comment(text_a2, self.u3, ref_object, parent=c1, minutes=20)
    #     a2.save()
    #     temp = "{% render_comment_list for reference %}"
    #     context = {'reference': ref_object}
    #     rendered = self.call_render(temp, context)
    #     print(rendered)
    #     self.assertTrue(text_c1 in rendered)
    #     self.assertTrue(text_a1 in rendered)
    #     self.assertTrue(text_a2 in rendered)


class PersistentTestData:
    """
    for playing around in the shell
    """
    def __init__(self):
        self.user_generator = dummy_user_generator()

        self.u1 = next(self.user_generator)
        self.u1.save()
        self.u2 = next(self.user_generator)
        self.u2.save()
        self.u3 = next(self.user_generator)
        self.u3.save()

        self.ref_object = CommentReferenceObject()
        self.ref_object.save()
        self.text_c1 = "telephone booth is magic"
        self.c1 = create_comment(self.text_c1, self.u1, self.ref_object, days=5)
        self.c1.save()
        self.text_a1 = "yeah, i can even see the star dust"
        self.a1 = create_comment(self.text_a1, self.u2, self.ref_object, parent=self.c1, days=2)
        self.a1.save()
        self.text_a2 = "i am also like this huge fan of phone booths"
        self.a2 = create_comment(self.text_a2, self.u3, self.ref_object, parent=self.c1, minutes=20)
        self.a2.save()
        self.temp = "{% render_comment_list for reference %}"
        self.context = {'reference': self.ref_object}
        self.rendered = TagTests.call_render(self.temp, self.context)
