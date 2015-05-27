"""
AuroraUser model method tests
"""

from datetime import datetime

from django.test import TestCase, Client

from AuroraUser.models import AuroraUser
from Stack.models import Stack, StackChallengeRelation
from Course.models import Course, CourseUserRelation
from Challenge.models import Challenge
from ReviewQuestion.models import ReviewQuestion
from Elaboration.models import Elaboration
from Review.models import Review
from django.conf import settings
from hashlib import sha1
from hmac import new as hmac_new


class AuroraUserTest(TestCase):
    def setUp(self):
        self.create_test_users(4)
        self.create_course()
        self.create_stack()
        self.create_challenge()
        self.create_review_question()

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

    def create_stack(self):
        self.stack = Stack(title="test stack", description="test description", course=self.course)
        self.stack.save()

    def create_challenge(self):
        self.challenge = Challenge(
            title='test_title',
            subtitle='test_subtitle',
            description='test_description',
            course=self.course,
        )
        self.challenge.save()
        StackChallengeRelation(stack=self.stack, challenge=self.challenge).save()

    def create_review_question(self):
        self.review_question = ReviewQuestion(
            challenge=self.challenge,
            order=1,
            text="Can you find any additional material not included in this submission?"
        )
        self.review_question.save()

    def create_review(self, elaboration, reviewer):
        Review(elaboration=elaboration, submission_time=datetime.now(), reviewer=reviewer, appraisal='S').save()

    @staticmethod
    def ipython_test():
        user = AuroraUser.objects.get(username='dd')
        c = Client()

        shared_secret = settings.SSO_SHARED_SECRET.encode(encoding='latin1')
        oid = '258'
        now = int((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds() / 10)

        values_string = oid + user.matriculation_number + user.first_name + user.last_name + user.email + str(now)
        hmac_calced = hmac_new(shared_secret, values_string.encode(encoding='latin1'), sha1).hexdigest()
        values = {'oid': oid,
                  'mn': user.matriculation_number,
                  'firstName': user.first_name,
                  'lastName': user.last_name,
                  'mail': user.email,
                  'sKey': hmac_calced}

        # response = c.get('sso_auth_callback', values, follow=True)

        from django.http import QueryDict
        q = QueryDict('', mutable=True)
        for key in values.keys():
            q[key] = values[key]
        url = 'http://localhost:8000/sso_auth_callback?' + q.urlencode()
        return url

    def test_sso(self):
        c = Client()

        shared_secret = settings.SSO_SHARED_SECRET.encode(encoding='latin1')
        oid = '258'
        user = self.users[0]
        now = int((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds() / 10)

        values_string = oid + user.matriculation_number + user.first_name + user.last_name + user.email + str(now)
        hmac_calced = hmac_new(shared_secret, values_string.encode(encoding='latin1'), sha1).hexdigest()
        values = {'oid': oid,
                  'mn': user.matriculation_number,
                  'firstName': user.first_name,
                  'lastName': user.last_name,
                  'mail': user.email,
                  'sKey': hmac_calced}

        response = c.get('sso_auth_callback', values, follow=True)

    def test_get_elaborations(self):
        challenge1 = self.challenge
        self.create_challenge()
        challenge2 = self.challenge
        challenge2.prerequisite = challenge1
        challenge2.save()
        self.create_challenge()
        challenge3 = self.challenge
        challenge3.prerequisite = challenge2
        challenge3.save()
        user1 = self.users[0]
        user2 = self.users[1]
        user3 = self.users[2]
        user4 = self.users[3]
        assert len(user1.get_elaborations()) == 0
        assert len(user2.get_elaborations()) == 0
        assert len(user3.get_elaborations()) == 0
        assert len(user4.get_elaborations()) == 0
        elaboration1 = Elaboration(challenge=challenge1, user=user1, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration1.save()
        assert len(user1.get_elaborations()) == 1
        assert elaboration1 in user1.get_elaborations()
        elaboration2 = Elaboration(challenge=challenge1, user=user2, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration2.save()
        assert len(user2.get_elaborations()) == 1
        assert elaboration2 in user2.get_elaborations()
        elaboration3 = Elaboration(challenge=challenge1, user=user3, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration3.save()
        assert len(user3.get_elaborations()) == 1
        assert elaboration3 in user3.get_elaborations()
        elaboration4 = Elaboration(challenge=challenge1, user=user4, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration4.save()
        assert len(user4.get_elaborations()) == 1
        assert elaboration4 in user4.get_elaborations()
        Review(elaboration=elaboration2, submission_time=datetime.now(), reviewer=user1,
               appraisal=Review.SUCCESS).save()
        Review(elaboration=elaboration3, submission_time=datetime.now(), reviewer=user1,
               appraisal=Review.SUCCESS).save()
        Review(elaboration=elaboration4, submission_time=datetime.now(), reviewer=user1,
               appraisal=Review.SUCCESS).save()
        Review(elaboration=elaboration1, submission_time=datetime.now(), reviewer=user2,
               appraisal=Review.SUCCESS).save()
        Review(elaboration=elaboration1, submission_time=datetime.now(), reviewer=user3,
               appraisal=Review.SUCCESS).save()
        elaboration5 = Elaboration(challenge=challenge2, user=user1, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration5.save()
        assert len(user1.get_elaborations()) == 2
        assert elaboration1 in user1.get_elaborations()
        assert elaboration5 in user1.get_elaborations()
        elaboration6 = Elaboration(challenge=challenge2, user=user2, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration6.save()
        assert len(user2.get_elaborations()) == 2
        assert elaboration2 in user2.get_elaborations()
        assert elaboration6 in user2.get_elaborations()
        elaboration7 = Elaboration(challenge=challenge2, user=user3, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration7.save()
        assert len(user3.get_elaborations()) == 2
        assert elaboration3 in user3.get_elaborations()
        assert elaboration7 in user3.get_elaborations()
        elaboration8 = Elaboration(challenge=challenge2, user=user4, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration8.save()
        assert len(user4.get_elaborations()) == 2
        assert elaboration4 in user4.get_elaborations()
        assert elaboration8 in user4.get_elaborations()

    def test_get_challenge_elaboration(self):
        challenge1 = self.challenge
        self.create_challenge()
        challenge2 = self.challenge
        challenge2.prerequisite = challenge1
        challenge2.save()
        self.create_challenge()
        challenge3 = self.challenge
        challenge3.prerequisite = challenge2
        challenge3.save()
        user1 = self.users[0]
        user2 = self.users[1]
        user3 = self.users[2]
        user4 = self.users[3]
        assert not user1.get_challenge_elaboration(challenge1)
        assert not user2.get_challenge_elaboration(challenge1)
        assert not user3.get_challenge_elaboration(challenge1)
        assert not user4.get_challenge_elaboration(challenge1)
        elaboration1 = Elaboration(challenge=challenge1, user=user1, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration1.save()
        elaboration2 = Elaboration(challenge=challenge1, user=user2, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration2.save()
        elaboration3 = Elaboration(challenge=challenge1, user=user3, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration3.save()
        elaboration4 = Elaboration(challenge=challenge1, user=user4, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration4.save()
        assert user1.get_challenge_elaboration(challenge1) == elaboration1
        assert user2.get_challenge_elaboration(challenge1) == elaboration2
        assert user3.get_challenge_elaboration(challenge1) == elaboration3
        assert user4.get_challenge_elaboration(challenge1) == elaboration4
        Review(elaboration=elaboration2, submission_time=datetime.now(), reviewer=user1,
               appraisal=Review.SUCCESS).save()
        Review(elaboration=elaboration3, submission_time=datetime.now(), reviewer=user1,
               appraisal=Review.SUCCESS).save()
        Review(elaboration=elaboration4, submission_time=datetime.now(), reviewer=user1,
               appraisal=Review.SUCCESS).save()
        Review(elaboration=elaboration1, submission_time=datetime.now(), reviewer=user2,
               appraisal=Review.SUCCESS).save()
        Review(elaboration=elaboration1, submission_time=datetime.now(), reviewer=user3,
               appraisal=Review.SUCCESS).save()
        assert not user1.get_challenge_elaboration(challenge2)
        assert not user2.get_challenge_elaboration(challenge2)
        assert not user3.get_challenge_elaboration(challenge2)
        assert not user4.get_challenge_elaboration(challenge2)
        elaboration5 = Elaboration(challenge=challenge2, user=user1, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration5.save()
        elaboration6 = Elaboration(challenge=challenge2, user=user2, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration6.save()
        elaboration7 = Elaboration(challenge=challenge2, user=user3, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration7.save()
        elaboration8 = Elaboration(challenge=challenge2, user=user4, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration8.save()
        assert user1.get_challenge_elaboration(challenge2) == elaboration5
        assert user2.get_challenge_elaboration(challenge2) == elaboration6
        assert user3.get_challenge_elaboration(challenge2) == elaboration7
        assert user4.get_challenge_elaboration(challenge2) == elaboration8

    def test_get_stack_elaborations(self):
        challenge1 = self.challenge
        self.create_challenge()
        challenge2 = self.challenge
        challenge2.prerequisite = challenge1
        challenge2.save()
        self.create_challenge()
        challenge3 = self.challenge
        challenge3.prerequisite = challenge2
        challenge3.save()
        user1 = self.users[0]
        user2 = self.users[1]
        user3 = self.users[2]
        user4 = self.users[3]
        assert len(user1.get_stack_elaborations(self.stack)) == 0
        assert len(user2.get_stack_elaborations(self.stack)) == 0
        assert len(user3.get_stack_elaborations(self.stack)) == 0
        assert len(user4.get_stack_elaborations(self.stack)) == 0
        elaboration1 = Elaboration(challenge=challenge1, user=user1, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration1.save()
        elaboration2 = Elaboration(challenge=challenge1, user=user2, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration2.save()
        elaboration3 = Elaboration(challenge=challenge1, user=user3, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration3.save()
        elaboration4 = Elaboration(challenge=challenge1, user=user4, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration4.save()
        assert len(user1.get_stack_elaborations(self.stack)) == 1
        assert len(user2.get_stack_elaborations(self.stack)) == 1
        assert len(user3.get_stack_elaborations(self.stack)) == 1
        assert len(user4.get_stack_elaborations(self.stack)) == 1
        assert elaboration1 in user1.get_stack_elaborations(self.stack)
        assert elaboration2 in user2.get_stack_elaborations(self.stack)
        assert elaboration3 in user3.get_stack_elaborations(self.stack)
        assert elaboration4 in user4.get_stack_elaborations(self.stack)
        Review(elaboration=elaboration2, submission_time=datetime.now(), reviewer=user1,
               appraisal=Review.SUCCESS).save()
        Review(elaboration=elaboration3, submission_time=datetime.now(), reviewer=user1,
               appraisal=Review.SUCCESS).save()
        Review(elaboration=elaboration4, submission_time=datetime.now(), reviewer=user1,
               appraisal=Review.SUCCESS).save()
        Review(elaboration=elaboration1, submission_time=datetime.now(), reviewer=user2,
               appraisal=Review.SUCCESS).save()
        Review(elaboration=elaboration1, submission_time=datetime.now(), reviewer=user3,
               appraisal=Review.SUCCESS).save()
        elaboration5 = Elaboration(challenge=challenge2, user=user1, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration5.save()
        elaboration6 = Elaboration(challenge=challenge2, user=user2, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration6.save()
        elaboration7 = Elaboration(challenge=challenge2, user=user3, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration7.save()
        elaboration8 = Elaboration(challenge=challenge2, user=user4, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration8.save()
        assert len(user1.get_stack_elaborations(self.stack)) == 2
        assert len(user2.get_stack_elaborations(self.stack)) == 2
        assert len(user3.get_stack_elaborations(self.stack)) == 2
        assert len(user4.get_stack_elaborations(self.stack)) == 2
        assert elaboration1 in user1.get_stack_elaborations(self.stack)
        assert elaboration2 in user2.get_stack_elaborations(self.stack)
        assert elaboration3 in user3.get_stack_elaborations(self.stack)
        assert elaboration4 in user4.get_stack_elaborations(self.stack)
        assert elaboration5 in user1.get_stack_elaborations(self.stack)
        assert elaboration6 in user2.get_stack_elaborations(self.stack)
        assert elaboration7 in user3.get_stack_elaborations(self.stack)
        assert elaboration8 in user4.get_stack_elaborations(self.stack)