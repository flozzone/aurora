from django.test import TestCase
from Comments.models import Comment
from PortfolioUser.models import PortfolioUser
from django.utils import timezone


def create_comment(text, author, days=0, minutes=0, seconds=0):
    delta = timezone.timedelta(days=-days, seconds=-(minutes*60) + seconds)
    post_date = timezone.now() + delta
    comment = Comment.objects.create(text=text, author=author, post_date=post_date)
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


class CommentMethodTests(TestCase):
    user_generator = dummy_user_generator()

    def test_post_date_relative_days_ago(self):
        u = self.user_generator.next()
        u.save()
        c = create_comment("helo und so", u, days=2, minutes=8)
        c.save()
        self.assertEqual(c.post_date_relative, "2 days ago")
