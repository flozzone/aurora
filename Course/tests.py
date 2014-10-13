"""
Course model method tests
"""

from datetime import datetime

from django.test import TestCase

from AuroraUser.models import AuroraUser
from Stack.models import Stack, StackChallengeRelation
from Course.models import Course, CourseUserRelation, CourseChallengeRelation
from Challenge.models import Challenge
from ReviewQuestion.models import ReviewQuestion
from Elaboration.models import Elaboration
from Evaluation.models import Evaluation
from Review.models import Review


class CourseTest(TestCase):
    def setUp(self):
        self.create_test_users(4)
        self.create_course()
        self.create_stack()
        self.create_challenge()

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

    def create_stack(self):
        self.stack = Stack(title="test stack", description="test description", course=self.course)
        self.stack.save()

    def create_challenge(self):
        self.challenge = Challenge(
            title='test_title',
            subtitle='test_subtitle',
            description='test_description',
        )
        self.challenge.save()
        CourseChallengeRelation(course=self.course, challenge=self.challenge).save()
        StackChallengeRelation(stack=self.stack, challenge=self.challenge).save()

    def test_user_is_enlisted(self):
        # created users should be enlisted in to the course
        assert self.course.user_is_enlisted(self.users[0])
        # created users should not be enlisted in any course yet
        user = self.create_test_user("test_user")
        course1 = self.course
        course2 = Course(
            title='test_title2',
            short_title='test_short_title2',
            description='test_description2',
            course_number='test_course_number2',
        )
        course2.save()
        assert not course1.user_is_enlisted(user)
        assert not course2.user_is_enlisted(user)
        # user should be enlisted in course1
        CourseUserRelation(course=course1, user=user).save()
        assert course1.user_is_enlisted(user)
        assert not course2.user_is_enlisted(user)
        # user should be enlisted in both courses
        CourseUserRelation(course=course2, user=user).save()
        assert course1.user_is_enlisted(user)
        assert course2.user_is_enlisted(user)

    def test_get_course_challenges(self):
        challenge1 = self.challenge
        assert len(self.course.get_course_challenges()) == 1
        assert challenge1 in self.course.get_course_challenges()

        self.create_challenge()
        challenge2 = self.challenge
        challenge2.prerequisite = challenge1
        challenge2.save()
        assert len(self.course.get_course_challenges()) == 2
        assert challenge1 in self.course.get_course_challenges()
        assert challenge2 in self.course.get_course_challenges()

        self.create_challenge()
        challenge3 = self.challenge
        challenge3.prerequisite = challenge2
        challenge3.save()
        assert len(self.course.get_course_challenges()) == 3
        assert challenge1 in self.course.get_course_challenges()
        assert challenge2 in self.course.get_course_challenges()
        assert challenge3 in self.course.get_course_challenges()
