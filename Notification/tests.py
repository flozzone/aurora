from django.test import TestCase

from Notification.models import Notification
from AuroraUser.models import AuroraUser
from Course.models import Course, CourseUserRelation


class NotificationTest(TestCase):
    def create_test_user(self, username):
        user = AuroraUser(username=username)
        user.email = '%s@student.tuwien.ac.at.' % username
        user.first_name = 'Firstname_%s' % username
        user.last_name = 'Lastname_%s' % username
        user.nickname = 'Nickname_%s' % username
        user.is_staff = False
        user.is_superuser = False
        password = username
        user.set_password(password)
        user.matriculation_number = username + '2857289'
        user.save()
        return user

    def create_test_users(self, amount):
        self.users = []
        for i in range(amount):
            self.users.append(self.create_test_user("s%s" % i))

    def create_course(self):
        self.course = Course(
            title='test_title',
            short_title='test_short_title',
            description='test_description',
            course_number='test_course_number',
        )
        self.course.save()
        for user in self.users:
            CourseUserRelation(course=self.course, user=user).save()

    def setUp(self):
        self.create_test_users(4)
        self.create_course()

    def test_text(self):
        user = self.users[0]
        text = Notification.truncate_text("test")
        obj, created = Notification.objects.get_or_create(
            user=user,
            course=self.course,
            text=text,
            image_url='test_image_url',
            link='test_link'
        )
        assert obj.text == text
        assert len(obj.text) <= 100

    def test_text_too_long(self):
        user = self.users[0]
        text = Notification.truncate_text("test" * 100)
        obj, created = Notification.objects.get_or_create(
            user=user,
            course=self.course,
            text=text,
            image_url='test_image_url',
            link='test_link'
        )
        assert obj.text == text
        assert len(obj.text) <= 100
        assert text[-3:] == '...'