"""
Elaboration model method tests
"""

from datetime import datetime, timedelta
import django

from django.test import TestCase

from AuroraUser.models import AuroraUser
from Course.models import Course, CourseUserRelation
from Stack.models import Stack, StackChallengeRelation
from Challenge.models import Challenge
from Review.models import Review
from ReviewQuestion.models import ReviewQuestion
from Elaboration.models import Elaboration
from Evaluation.models import Evaluation


class ElaborationTest(TestCase):
    def setUp(self):
        self.create_test_users(5)
        self.create_dummy_users(3)
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
        user.save()
        return user

    def create_dummy_user(self, username):
        user = self.create_test_user(username)
        user.is_staff = True
        user.save()
        return user

    def create_test_users(self, amount):
        self.users = []
        for i in range(amount):
            self.users.append(self.create_test_user("s%s" % i))

    def create_dummy_users(self, amount):
        self.dummy_users = []
        for i in range(amount):
            self.dummy_users.append(self.create_dummy_user("d%s" % i))


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

    def test_get_review_candidate_prefer_real_users(self):
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
        dummy_user1 = self.dummy_users[0]
        dummy_user2 = self.dummy_users[1]
        dummy_user3 = self.dummy_users[2]
        elaboration1 = Elaboration(challenge=challenge1, user=user1, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration1.save()
        dummy_elaboration1 = Elaboration(challenge=challenge1, user=dummy_user1, elaboration_text="test",
                                         submission_time=datetime.now())
        dummy_elaboration1.save()
        dummy_elaboration2 = Elaboration(challenge=challenge1, user=dummy_user2, elaboration_text="test",
                                         submission_time=datetime.now())
        dummy_elaboration2.save()
        dummy_elaboration3 = Elaboration(challenge=challenge1, user=dummy_user3, elaboration_text="test",
                                         submission_time=datetime.now())
        dummy_elaboration3.save()
        # first user will get the dummy_elaboration because the only real elaboration is his own
        # all other users will the the real elaboration from user 1
        assert Elaboration.get_review_candidate(challenge1, user1) == dummy_elaboration1
        assert Elaboration.get_review_candidate(challenge1, user2) == elaboration1
        assert Elaboration.get_review_candidate(challenge1, user3) == elaboration1
        assert Elaboration.get_review_candidate(challenge1, user4) == elaboration1
        elaboration2 = Elaboration(challenge=challenge1, user=user2, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration2.save()
        # first user will get the elaboration from user 2 because
        # all other users will the the real elaboration from user 1 because it has the lowest id
        assert Elaboration.get_review_candidate(challenge1, user1) == elaboration2
        assert Elaboration.get_review_candidate(challenge1, user2) == elaboration1
        assert Elaboration.get_review_candidate(challenge1, user3) == elaboration1
        assert Elaboration.get_review_candidate(challenge1, user4) == elaboration1
        elaboration3 = Elaboration(challenge=challenge1, user=user3, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration3.save()
        # adding another elaboration does not change the outcome
        # if no other conditions apply the first database entry will be used (item with lowest id)
        assert Elaboration.get_review_candidate(challenge1, user1) == elaboration2
        assert Elaboration.get_review_candidate(challenge1, user2) == elaboration1
        assert Elaboration.get_review_candidate(challenge1, user3) == elaboration1
        assert Elaboration.get_review_candidate(challenge1, user4) == elaboration1

    def test_get_review_candidate_real_scenario(self):
        user1 = self.users[0]
        user2 = self.users[1]
        dummy_user1 = self.dummy_users[0]
        dummy_user2 = self.dummy_users[1]
        dummy_user3 = self.dummy_users[2]
        dummy_elaboration1 = Elaboration(challenge=self.challenge, user=dummy_user1, elaboration_text="test",
                                         submission_time=datetime.now())
        dummy_elaboration1.save()
        dummy_elaboration2 = Elaboration(challenge=self.challenge, user=dummy_user2, elaboration_text="test",
                                         submission_time=datetime.now())
        dummy_elaboration2.save()
        dummy_elaboration3 = Elaboration(challenge=self.challenge, user=dummy_user3, elaboration_text="test",
                                         submission_time=datetime.now())
        dummy_elaboration3.save()
        # first user writes an elaboration
        elaboration1 = Elaboration(challenge=self.challenge, user=user1, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration1.save()
        assert Elaboration.get_review_candidate(self.challenge, user1) == dummy_elaboration1
        Review(elaboration=dummy_elaboration1, reviewer=user1, appraisal='S', submission_time=datetime.now()).save()
        assert Elaboration.get_review_candidate(self.challenge, user1) == dummy_elaboration2
        Review(elaboration=dummy_elaboration2, reviewer=user1, appraisal='S', submission_time=datetime.now()).save()
        assert Elaboration.get_review_candidate(self.challenge, user1) == dummy_elaboration3
        Review(elaboration=dummy_elaboration3, reviewer=user1, appraisal='S', submission_time=datetime.now()).save()
        # second user writes an elaboration
        elaboration2 = Elaboration(challenge=self.challenge, user=user2, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration2.save()
        assert Elaboration.get_review_candidate(self.challenge, user2) == elaboration1
        Review(elaboration=elaboration1, reviewer=user2, appraisal='S', submission_time=datetime.now()).save()
        assert Elaboration.get_review_candidate(self.challenge, user2) == dummy_elaboration1
        Review(elaboration=dummy_elaboration1, reviewer=user2, appraisal='S', submission_time=datetime.now()).save()
        assert Elaboration.get_review_candidate(self.challenge, user2) == dummy_elaboration2
        Review(elaboration=dummy_elaboration2, reviewer=user2, appraisal='S', submission_time=datetime.now()).save()

    def test_get_review_candidate_less_reviews(self):
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
        dummy_user1 = self.dummy_users[0]
        dummy_user2 = self.dummy_users[1]
        dummy_user3 = self.dummy_users[2]
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
        dummy_elaboration1 = Elaboration(challenge=challenge1, user=dummy_user1, elaboration_text="test",
                                         submission_time=datetime.now())
        dummy_elaboration1.save()
        dummy_elaboration2 = Elaboration(challenge=challenge1, user=dummy_user2, elaboration_text="test",
                                         submission_time=datetime.now())
        dummy_elaboration2.save()
        dummy_elaboration3 = Elaboration(challenge=challenge1, user=dummy_user3, elaboration_text="test",
                                         submission_time=datetime.now())
        dummy_elaboration3.save()
        assert Elaboration.get_review_candidate(challenge1, user1) == elaboration2  # 2 because 1 is own
        assert Elaboration.get_review_candidate(challenge1, user2) == elaboration1  # 1 because first
        assert Elaboration.get_review_candidate(challenge1, user3) == elaboration1  # 1 because first
        assert Elaboration.get_review_candidate(challenge1, user4) == elaboration1  # 1 because first
        Review(elaboration=elaboration2, submission_time=datetime.now(), reviewer=dummy_user1,
               appraisal=Review.SUCCESS).save()
        assert Elaboration.get_review_candidate(challenge1, user1) == elaboration3  # 3 because 2 has now 1 review
        assert Elaboration.get_review_candidate(challenge1, user2) == elaboration1  # 1 because first
        assert Elaboration.get_review_candidate(challenge1, user3) == elaboration1  # 1 because first
        assert Elaboration.get_review_candidate(challenge1, user4) == elaboration1  # 1 because first
        Review(elaboration=elaboration1, submission_time=datetime.now(), reviewer=dummy_user1,
               appraisal=Review.SUCCESS).save()
        assert Elaboration.get_review_candidate(challenge1, user1) == elaboration3  # 3 because nothing changed
        assert Elaboration.get_review_candidate(challenge1, user2) == elaboration3  # 3 1 and 2 have 1 review
        assert Elaboration.get_review_candidate(challenge1, user3) == elaboration4  # 4 because 3 is own
        assert Elaboration.get_review_candidate(challenge1, user4) == elaboration3  # 3 1 and 2 have 1 review
        Review(elaboration=elaboration4, submission_time=datetime.now(), reviewer=dummy_user1,
               appraisal=Review.SUCCESS).save()
        assert Elaboration.get_review_candidate(challenge1, user1) == elaboration3  # 3 because nothing changed
        assert Elaboration.get_review_candidate(challenge1, user2) == elaboration3  # 3 because nothing changed
        assert Elaboration.get_review_candidate(challenge1, user3) == elaboration1  # 1 because first
        assert Elaboration.get_review_candidate(challenge1, user4) == elaboration3  # 3 because nothing changed

    def test_get_review_candidate_sequential(self):
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
        dummy_user1 = self.dummy_users[0]
        dummy_user2 = self.dummy_users[1]
        dummy_user3 = self.dummy_users[2]
        dummy_elaboration1 = Elaboration(challenge=challenge1, user=dummy_user1, elaboration_text="test",
                                         submission_time=datetime.now())
        dummy_elaboration1.save()
        dummy_elaboration2 = Elaboration(challenge=challenge1, user=dummy_user2, elaboration_text="test",
                                         submission_time=datetime.now())
        dummy_elaboration2.save()
        dummy_elaboration3 = Elaboration(challenge=challenge1, user=dummy_user3, elaboration_text="test",
                                         submission_time=datetime.now())
        dummy_elaboration3.save()
        # this is what a clean start would look like
        # entering student 1
        elaboration1 = Elaboration(challenge=challenge1, user=user1, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration1.save()
        assert Elaboration.get_review_candidate(challenge1, user1) == dummy_elaboration1  # no elaborations there yet
        Review(elaboration=Elaboration.get_review_candidate(challenge1, user1), submission_time=datetime.now(),
               reviewer=user1, appraisal=Review.SUCCESS).save()
        assert Elaboration.get_review_candidate(challenge1, user1) == dummy_elaboration2  # no elaborations there yet
        Review(elaboration=Elaboration.get_review_candidate(challenge1, user1), submission_time=datetime.now(),
               reviewer=user1, appraisal=Review.SUCCESS).save()
        assert Elaboration.get_review_candidate(challenge1, user1) == dummy_elaboration3  # no elaborations there yet
        Review(elaboration=Elaboration.get_review_candidate(challenge1, user1), submission_time=datetime.now(),
               reviewer=user1, appraisal=Review.SUCCESS).save()
        # entering student 2
        elaboration2 = Elaboration(challenge=challenge1, user=user2, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration2.save()
        assert Elaboration.get_review_candidate(challenge1, user2) == elaboration1  # get real user elaboration 1
        Review(elaboration=Elaboration.get_review_candidate(challenge1, user2), submission_time=datetime.now(),
               reviewer=user2, appraisal=Review.SUCCESS).save()
        assert Elaboration.get_review_candidate(challenge1, user2) == dummy_elaboration1  # no elaborations left
        Review(elaboration=Elaboration.get_review_candidate(challenge1, user2), submission_time=datetime.now(),
               reviewer=user2, appraisal=Review.SUCCESS).save()
        assert Elaboration.get_review_candidate(challenge1, user2) == dummy_elaboration2  # no elaborations left
        Review(elaboration=Elaboration.get_review_candidate(challenge1, user2), submission_time=datetime.now(),
               reviewer=user2, appraisal=Review.SUCCESS).save()
        # entering student 3
        elaboration3 = Elaboration(challenge=challenge1, user=user3, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration3.save()
        assert Elaboration.get_review_candidate(challenge1, user3) == elaboration2  # get real user elaboration 2
        Review(elaboration=Elaboration.get_review_candidate(challenge1, user3), submission_time=datetime.now(),
               reviewer=user3, appraisal=Review.SUCCESS).save()
        assert Elaboration.get_review_candidate(challenge1, user3) == elaboration1  # get real user elaboration 1
        Review(elaboration=Elaboration.get_review_candidate(challenge1, user3), submission_time=datetime.now(),
               reviewer=user3, appraisal=Review.SUCCESS).save()
        assert Elaboration.get_review_candidate(challenge1, user3) == dummy_elaboration3  # least reviews
        Review(elaboration=Elaboration.get_review_candidate(challenge1, user3), submission_time=datetime.now(),
               reviewer=user3, appraisal=Review.SUCCESS).save()
        # entering student 4 which will be the first one to not receive a dummy elaboration
        elaboration4 = Elaboration(challenge=challenge1, user=user4, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration4.save()
        assert Elaboration.get_review_candidate(challenge1, user4) == elaboration3  # least review
        Review(elaboration=Elaboration.get_review_candidate(challenge1, user4), submission_time=datetime.now(),
               reviewer=user4, appraisal=Review.SUCCESS).save()
        assert Elaboration.get_review_candidate(challenge1, user4) == elaboration2  # less review
        Review(elaboration=Elaboration.get_review_candidate(challenge1, user4), submission_time=datetime.now(),
               reviewer=user4, appraisal=Review.SUCCESS).save()
        assert Elaboration.get_review_candidate(challenge1, user4) == elaboration1  # last candidate left
        Review(elaboration=Elaboration.get_review_candidate(challenge1, user4), submission_time=datetime.now(),
               reviewer=user4, appraisal=Review.SUCCESS).save()

    def test_get_review_candidate_parallel(self):
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
        dummy_user1 = self.dummy_users[0]
        dummy_user2 = self.dummy_users[1]
        dummy_user3 = self.dummy_users[2]
        dummy_elaboration1 = Elaboration(challenge=challenge1, user=dummy_user1, elaboration_text="test",
                                         submission_time=datetime.now())
        dummy_elaboration1.save()
        dummy_elaboration2 = Elaboration(challenge=challenge1, user=dummy_user2, elaboration_text="test",
                                         submission_time=datetime.now())
        dummy_elaboration2.save()
        dummy_elaboration3 = Elaboration(challenge=challenge1, user=dummy_user3, elaboration_text="test",
                                         submission_time=datetime.now())
        dummy_elaboration3.save()
        # this is what a clean start would look like

        # entering student 1 -------------------------------------------------------------------------------------------
        elaboration1 = Elaboration(challenge=challenge1, user=user1, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration1.save()
        assert Elaboration.get_review_candidate(challenge1, user1) == dummy_elaboration1
        assert Elaboration.get_review_candidate(challenge1, user2) == elaboration1
        assert Elaboration.get_review_candidate(challenge1, user3) == elaboration1
        assert Elaboration.get_review_candidate(challenge1, user4) == elaboration1
        # Review for dummy_elaboration1
        Review(elaboration=Elaboration.get_review_candidate(challenge1, user1), submission_time=datetime.now(),
               reviewer=user1, appraisal=Review.SUCCESS).save()
        assert Elaboration.get_review_candidate(challenge1, user1) == dummy_elaboration2
        assert Elaboration.get_review_candidate(challenge1, user2) == elaboration1
        assert Elaboration.get_review_candidate(challenge1, user3) == elaboration1
        assert Elaboration.get_review_candidate(challenge1, user4) == elaboration1
        # opens review but does not submit it yet
        # Review for dummy_elaboration2
        Review(elaboration=Elaboration.get_review_candidate(challenge1, user1), reviewer=user1).save()
        assert Elaboration.get_review_candidate(challenge1, user1) == dummy_elaboration3
        assert Elaboration.get_review_candidate(challenge1, user2) == elaboration1
        assert Elaboration.get_review_candidate(challenge1, user3) == elaboration1
        assert Elaboration.get_review_candidate(challenge1, user4) == elaboration1

        # entering student 2 -------------------------------------------------------------------------------------------
        elaboration2 = Elaboration(challenge=challenge1, user=user2, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration2.save()
        assert Elaboration.get_review_candidate(challenge1, user1) == elaboration2
        assert Elaboration.get_review_candidate(challenge1, user2) == elaboration1
        assert Elaboration.get_review_candidate(challenge1, user3) == elaboration1
        assert Elaboration.get_review_candidate(challenge1, user4) == elaboration1
        # Review for elaboration1
        Review(elaboration=Elaboration.get_review_candidate(challenge1, user2), submission_time=datetime.now(),
               reviewer=user2, appraisal=Review.SUCCESS).save()
        assert Elaboration.get_review_candidate(challenge1, user1) == elaboration2
        assert Elaboration.get_review_candidate(challenge1, user2) == dummy_elaboration3
        assert Elaboration.get_review_candidate(challenge1, user3) == elaboration2
        assert Elaboration.get_review_candidate(challenge1, user4) == elaboration2
        # opens review but does not submit it yet
        # Review for dummy_elaboration3
        Review(elaboration=Elaboration.get_review_candidate(challenge1, user2), reviewer=user2).save()
        assert Elaboration.get_review_candidate(challenge1, user1) == elaboration2
        assert Elaboration.get_review_candidate(challenge1, user2) == dummy_elaboration1
        assert Elaboration.get_review_candidate(challenge1, user3) == elaboration2
        assert Elaboration.get_review_candidate(challenge1, user4) == elaboration2
        # entering student 3 -------------------------------------------------------------------------------------------
        elaboration3 = Elaboration(challenge=challenge1, user=user3, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration3.save()
        assert Elaboration.get_review_candidate(challenge1, user1) == elaboration2
        assert Elaboration.get_review_candidate(challenge1, user2) == elaboration3
        assert Elaboration.get_review_candidate(challenge1, user3) == elaboration2
        assert Elaboration.get_review_candidate(challenge1, user4) == elaboration2
        # Review for elaboration2
        Review(elaboration=Elaboration.get_review_candidate(challenge1, user3), submission_time=datetime.now(),
               reviewer=user3, appraisal=Review.SUCCESS).save()
        assert Elaboration.get_review_candidate(challenge1, user1) == elaboration3
        assert Elaboration.get_review_candidate(challenge1, user2) == elaboration3
        assert Elaboration.get_review_candidate(challenge1, user3) == elaboration1
        assert Elaboration.get_review_candidate(challenge1, user4) == elaboration3
        # opens review but does not submit it yet
        # Review for elaborations1
        Review(elaboration=Elaboration.get_review_candidate(challenge1, user3), reviewer=user3).save()
        assert Elaboration.get_review_candidate(challenge1, user1) == elaboration3
        assert Elaboration.get_review_candidate(challenge1, user2) == elaboration3
        assert Elaboration.get_review_candidate(challenge1, user3) == dummy_elaboration1
        assert Elaboration.get_review_candidate(challenge1, user4) == elaboration3

        # entering student 4 which will be the first one to not receive a dummy elaboration ----------------------------
        elaboration4 = Elaboration(challenge=challenge1, user=user4, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration4.save()
        assert Elaboration.get_review_candidate(challenge1, user1) == elaboration3
        assert Elaboration.get_review_candidate(challenge1, user2) == elaboration3
        assert Elaboration.get_review_candidate(challenge1, user3) == elaboration4
        assert Elaboration.get_review_candidate(challenge1, user4) == elaboration3
        # Review for elaboration3
        Review(elaboration=Elaboration.get_review_candidate(challenge1, user4), submission_time=datetime.now(),
               reviewer=user4, appraisal=Review.SUCCESS).save()
        assert Elaboration.get_review_candidate(challenge1, user1) == elaboration4
        assert Elaboration.get_review_candidate(challenge1, user2) == elaboration4
        assert Elaboration.get_review_candidate(challenge1, user3) == elaboration4
        assert Elaboration.get_review_candidate(challenge1, user4) == elaboration2
        # opens review but does not submit it yet
        # Review for elaborations2
        Review(elaboration=Elaboration.get_review_candidate(challenge1, user4), reviewer=user4).save()
        assert Elaboration.get_review_candidate(challenge1, user1) == elaboration4
        assert Elaboration.get_review_candidate(challenge1, user2) == elaboration4
        assert Elaboration.get_review_candidate(challenge1, user3) == elaboration4
        assert Elaboration.get_review_candidate(challenge1, user4) == elaboration1

    def test_get_review_candidate_unsubmitted(self):
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
        dummy_user1 = self.dummy_users[0]
        dummy_user2 = self.dummy_users[1]
        dummy_user3 = self.dummy_users[2]
        dummy_elaboration1 = Elaboration(challenge=challenge1, user=dummy_user1, elaboration_text="test",
                                         submission_time=datetime.now())
        dummy_elaboration1.save()
        dummy_elaboration2 = Elaboration(challenge=challenge1, user=dummy_user2, elaboration_text="test",
                                         submission_time=datetime.now())
        dummy_elaboration2.save()
        dummy_elaboration3 = Elaboration(challenge=challenge1, user=dummy_user3, elaboration_text="test",
                                         submission_time=datetime.now())
        dummy_elaboration3.save()

        elaboration1 = Elaboration(challenge=challenge1, user=user1, elaboration_text="test")
        elaboration1.save()
        assert Elaboration.get_review_candidate(challenge1, user1) == dummy_elaboration1
        assert Elaboration.get_review_candidate(challenge1, user2) == dummy_elaboration1
        assert Elaboration.get_review_candidate(challenge1, user3) == dummy_elaboration1
        assert Elaboration.get_review_candidate(challenge1, user4) == dummy_elaboration1
        elaboration2 = Elaboration(challenge=challenge1, user=user2, elaboration_text="test")
        elaboration2.save()
        assert Elaboration.get_review_candidate(challenge1, user1) == dummy_elaboration1
        assert Elaboration.get_review_candidate(challenge1, user2) == dummy_elaboration1
        assert Elaboration.get_review_candidate(challenge1, user3) == dummy_elaboration1
        assert Elaboration.get_review_candidate(challenge1, user4) == dummy_elaboration1
        elaboration3 = Elaboration(challenge=challenge1, user=user3, elaboration_text="test")
        elaboration3.save()
        assert Elaboration.get_review_candidate(challenge1, user1) == dummy_elaboration1
        assert Elaboration.get_review_candidate(challenge1, user2) == dummy_elaboration1
        assert Elaboration.get_review_candidate(challenge1, user3) == dummy_elaboration1
        assert Elaboration.get_review_candidate(challenge1, user4) == dummy_elaboration1
        elaboration1.submission_time = datetime.now()
        elaboration1.save()
        assert Elaboration.get_review_candidate(challenge1, user1) == dummy_elaboration1
        assert Elaboration.get_review_candidate(challenge1, user2) == elaboration1
        assert Elaboration.get_review_candidate(challenge1, user3) == elaboration1
        assert Elaboration.get_review_candidate(challenge1, user4) == elaboration1
        elaboration2.submission_time = datetime.now()
        elaboration2.save()
        assert Elaboration.get_review_candidate(challenge1, user1) == elaboration2
        assert Elaboration.get_review_candidate(challenge1, user2) == elaboration1
        assert Elaboration.get_review_candidate(challenge1, user3) == elaboration1
        assert Elaboration.get_review_candidate(challenge1, user4) == elaboration1

    def test_is_reviewed_2times(self):
        user1 = self.users[0]
        user2 = self.users[1]
        user3 = self.users[2]
        challenge = self.challenge
        elaboration1 = Elaboration(challenge=challenge, user=user1, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration1.save()
        elaboration2 = Elaboration(challenge=challenge, user=user2, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration2.save()
        elaboration3 = Elaboration(challenge=challenge, user=user3, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration3.save()
        assert not elaboration1.is_reviewed_2times()
        assert not elaboration2.is_reviewed_2times()
        assert not elaboration3.is_reviewed_2times()
        Review(elaboration=elaboration1, submission_time=datetime.now(),
               reviewer=user2, appraisal=Review.SUCCESS).save()
        assert not elaboration1.is_reviewed_2times()
        assert not elaboration2.is_reviewed_2times()
        assert not elaboration3.is_reviewed_2times()
        Review(elaboration=elaboration1, submission_time=datetime.now(),
               reviewer=user3, appraisal=Review.SUCCESS).save()
        assert elaboration1.is_reviewed_2times()
        assert not elaboration2.is_reviewed_2times()
        assert not elaboration3.is_reviewed_2times()
        Review(elaboration=elaboration2, submission_time=datetime.now(),
               reviewer=user1, appraisal=Review.SUCCESS).save()
        assert elaboration1.is_reviewed_2times()
        assert not elaboration2.is_reviewed_2times()
        assert not elaboration3.is_reviewed_2times()
        review = Review(elaboration=elaboration2,
                        reviewer=user1, appraisal=Review.SUCCESS)
        review.save()
        assert elaboration1.is_reviewed_2times()
        assert not elaboration2.is_reviewed_2times()
        assert not elaboration3.is_reviewed_2times()
        review.submission_time = datetime.now()
        review.save()
        assert elaboration1.is_reviewed_2times()
        assert elaboration2.is_reviewed_2times()
        assert not elaboration3.is_reviewed_2times()
        review1 = Review(elaboration=elaboration3,
                         reviewer=user1, appraisal=Review.SUCCESS)
        review1.save()
        review2 = Review(elaboration=elaboration3,
                         reviewer=user2, appraisal=Review.SUCCESS)
        review2.save()
        assert elaboration1.is_reviewed_2times()
        assert elaboration2.is_reviewed_2times()
        assert not elaboration3.is_reviewed_2times()
        review1.submission_time = datetime.now()
        review1.save()
        assert elaboration1.is_reviewed_2times()
        assert elaboration2.is_reviewed_2times()
        assert not elaboration3.is_reviewed_2times()
        review2.submission_time = datetime.now()
        review2.save()
        assert elaboration1.is_reviewed_2times()
        assert elaboration2.is_reviewed_2times()
        assert elaboration3.is_reviewed_2times()

    def test_get_others(self):
        user1 = self.users[0]
        user2 = self.users[1]
        user3 = self.users[2]
        dummy_user1 = self.dummy_users[0]
        challenge = self.challenge
        elaboration1 = Elaboration(challenge=challenge, user=user1, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration1.save()
        elaboration2 = Elaboration(challenge=challenge, user=user2, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration2.save()
        assert elaboration1 not in elaboration1.get_others()
        assert elaboration2 in elaboration1.get_others()
        assert elaboration1 in elaboration2.get_others()
        assert elaboration2 not in elaboration2.get_others()
        elaboration3 = Elaboration(challenge=challenge, user=user3, elaboration_text="test")
        elaboration3.save()
        assert elaboration1 not in elaboration1.get_others()
        assert elaboration2 in elaboration1.get_others()
        assert elaboration3 not in elaboration1.get_others()
        assert elaboration1 in elaboration2.get_others()
        assert elaboration2 not in elaboration2.get_others()
        assert elaboration3 not in elaboration2.get_others()
        elaboration3.submission_time = datetime.now()
        elaboration3.save()
        assert elaboration1 not in elaboration1.get_others()
        assert elaboration2 in elaboration1.get_others()
        assert elaboration3 in elaboration1.get_others()
        assert elaboration1 in elaboration2.get_others()
        assert elaboration2 not in elaboration2.get_others()
        assert elaboration3 in elaboration2.get_others()
        assert elaboration1 in elaboration3.get_others()
        assert elaboration2 in elaboration3.get_others()
        assert elaboration3 not in elaboration3.get_others()
        dummy_elaboration1 = Elaboration(challenge=challenge, user=dummy_user1, elaboration_text="test",
                                         submission_time=datetime.now())
        dummy_elaboration1.save()
        assert elaboration1 not in elaboration1.get_others()
        assert elaboration2 in elaboration1.get_others()
        assert elaboration3 in elaboration1.get_others()
        assert elaboration1 in elaboration2.get_others()
        assert elaboration2 not in elaboration2.get_others()
        assert elaboration3 in elaboration2.get_others()
        assert elaboration1 in elaboration3.get_others()
        assert elaboration2 in elaboration3.get_others()
        assert elaboration3 not in elaboration3.get_others()

    def test_get_sel_challenge_elaborations(self):
        challenge1 = self.challenge
        self.create_challenge()
        challenge2 = self.challenge
        challenge2.prerequisite = challenge1
        challenge2.save()
        user1 = self.users[0]
        user2 = self.users[1]
        user3 = self.users[2]
        dummy_user1 = self.dummy_users[0]
        challenge = self.challenge
        elaboration1 = Elaboration(challenge=challenge1, user=user1, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration1.save()
        assert elaboration1 in Elaboration.get_sel_challenge_elaborations(challenge1)
        assert not Elaboration.get_sel_challenge_elaborations(challenge2)
        elaboration2 = Elaboration(challenge=challenge1, user=user2, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration2.save()
        assert elaboration1 in Elaboration.get_sel_challenge_elaborations(challenge1)
        assert elaboration2 in Elaboration.get_sel_challenge_elaborations(challenge1)
        assert not Elaboration.get_sel_challenge_elaborations(challenge2)

        elaboration3 = Elaboration(challenge=challenge1, user=user3, elaboration_text="test")
        elaboration3.save()
        assert elaboration1 in Elaboration.get_sel_challenge_elaborations(challenge1)
        assert elaboration2 in Elaboration.get_sel_challenge_elaborations(challenge1)
        assert elaboration3 not in Elaboration.get_sel_challenge_elaborations(challenge1)
        assert not Elaboration.get_sel_challenge_elaborations(challenge2)

        elaboration3.submission_time = datetime.now()
        elaboration3.save()

        assert elaboration1 in Elaboration.get_sel_challenge_elaborations(challenge1)
        assert elaboration2 in Elaboration.get_sel_challenge_elaborations(challenge1)
        assert elaboration3 in Elaboration.get_sel_challenge_elaborations(challenge1)
        assert not Elaboration.get_sel_challenge_elaborations(challenge2)

        assert not Elaboration.get_sel_challenge_elaborations(challenge2)
        elaboration4 = Elaboration(challenge=challenge2, user=user1, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration4.save()

        assert elaboration1 in Elaboration.get_sel_challenge_elaborations(challenge1)
        assert elaboration2 in Elaboration.get_sel_challenge_elaborations(challenge1)
        assert elaboration3 in Elaboration.get_sel_challenge_elaborations(challenge1)
        assert elaboration4 not in Elaboration.get_sel_challenge_elaborations(challenge1)
        assert Elaboration.get_sel_challenge_elaborations(challenge2)
        assert elaboration4 in Elaboration.get_sel_challenge_elaborations(challenge2)

    def test_get_missing_reviews(self):
        challenge1 = self.challenge
        self.create_challenge()
        challenge2 = self.challenge
        challenge2.prerequisite = challenge1
        challenge2.save()
        user1 = self.users[0]
        user2 = self.users[1]
        user3 = self.users[2]
        user4 = self.users[3]
        user5 = self.users[4]
        dummy_user1 = self.dummy_users[0]

        new = datetime.now()
        old = datetime.now() - timedelta(days=2)

        dummy_elaboration1 = Elaboration(challenge=challenge1, user=dummy_user1, elaboration_text="test",
                                         submission_time=old)
        dummy_elaboration1.save()
        elaboration1 = Elaboration(challenge=challenge1, user=user1, elaboration_text="test",
                                   submission_time=old)
        elaboration1.save()
        elaboration2 = Elaboration(challenge=challenge1, user=user2, elaboration_text="test",
                                   submission_time=new)
        elaboration2.save()
        elaboration3 = Elaboration(challenge=challenge1, user=user3, elaboration_text="test",
                                   submission_time=old)
        elaboration3.save()
        elaboration4 = Elaboration(challenge=challenge1, user=user4, elaboration_text="test")
        elaboration4.save()
        elaboration5 = Elaboration(challenge=challenge1, user=user5, elaboration_text="test",
                                   submission_time=old)
        elaboration5.save()
        elaboration6 = Elaboration(challenge=challenge2, user=user1, elaboration_text="test",
                                   submission_time=old)
        elaboration6.save()

        assert dummy_elaboration1 not in Elaboration.get_missing_reviews(self.course)  # is staff
        assert elaboration1 in Elaboration.get_missing_reviews(self.course)  # 2 reviews missing
        assert elaboration2 not in Elaboration.get_missing_reviews(self.course)  # not 3 days old
        assert elaboration3 in Elaboration.get_missing_reviews(self.course)  # 2 reviews missing
        assert elaboration4 not in Elaboration.get_missing_reviews(self.course)  # unsubmitted
        assert elaboration5 in Elaboration.get_missing_reviews(self.course)  # 2 reviews missing
        assert elaboration6 not in Elaboration.get_missing_reviews(self.course)  # final challenge

        Review(elaboration=elaboration1, reviewer=user2, appraisal='S', submission_time=new).save()
        Review(elaboration=elaboration1, reviewer=user3, appraisal='S', submission_time=new).save()
        Review(elaboration=elaboration2, reviewer=user1, appraisal='S', submission_time=new).save()
        Review(elaboration=elaboration5, reviewer=user1, appraisal='S', submission_time=new).save()

        assert dummy_elaboration1 not in Elaboration.get_missing_reviews(self.course)  # is staff
        assert elaboration1 not in Elaboration.get_missing_reviews(self.course)  # already 2 reviews
        assert elaboration2 not in Elaboration.get_missing_reviews(self.course)  # not 3 days old
        assert elaboration3 in Elaboration.get_missing_reviews(self.course)  # 2 reviews missing
        assert elaboration4 not in Elaboration.get_missing_reviews(self.course)  # unsubmitted
        assert elaboration5 in Elaboration.get_missing_reviews(self.course)  # 1 review missing
        assert elaboration6 not in Elaboration.get_missing_reviews(self.course)  # final challenge

        elaboration2.submission_time = old
        elaboration2.save()
        elaboration4.submission_time = old
        elaboration4.save()

        Review(elaboration=elaboration3, reviewer=user1, appraisal='S').save()
        Review(elaboration=elaboration3, reviewer=user2, appraisal='S').save()
        Review(elaboration=elaboration5, reviewer=user2, appraisal='S', submission_time=new).save()

        assert dummy_elaboration1 not in Elaboration.get_missing_reviews(self.course)  # is staff
        assert elaboration1 not in Elaboration.get_missing_reviews(self.course)  # already 2 reviews
        assert elaboration2 in Elaboration.get_missing_reviews(self.course)  # not 3 days old
        assert elaboration3 in Elaboration.get_missing_reviews(self.course)  # 2 reviews missing because reviews are unsubmitted
        assert elaboration4 in Elaboration.get_missing_reviews(self.course)  # 2 reviews missing
        assert elaboration5 not in Elaboration.get_missing_reviews(self.course)  # already 2 reviews
        assert elaboration6 not in Elaboration.get_missing_reviews(self.course)  # final challenge

    def test_get_missing_reviews_unsubmitted(self):
        challenge1 = self.challenge
        self.create_challenge()
        challenge2 = self.challenge
        challenge2.prerequisite = challenge1
        challenge2.save()
        user1 = self.users[0]
        user2 = self.users[1]
        user3 = self.users[2]
        user4 = self.users[3]
        user5 = self.users[4]
        dummy_user1 = self.dummy_users[0]

        old = datetime.now() - timedelta(days=3)

        dummy_elaboration1 = Elaboration(challenge=challenge1, user=dummy_user1, elaboration_text="test",
                                         submission_time=old)
        dummy_elaboration1.save()
        elaboration1 = Elaboration(challenge=challenge1, user=user1, elaboration_text="test",
                                   submission_time=old)
        elaboration1.save()
        elaboration2 = Elaboration(challenge=challenge1, user=user2, elaboration_text="test",
                                   submission_time=old)
        elaboration2.save()
        elaboration3 = Elaboration(challenge=challenge1, user=user3, elaboration_text="test",
                                   submission_time=old)
        elaboration3.save()
        elaboration4 = Elaboration(challenge=challenge1, user=user4, elaboration_text="test",
                                   submission_time=old)
        elaboration4.save()
        elaboration5 = Elaboration(challenge=challenge1, user=user5, elaboration_text="test",
                                   submission_time=old)
        elaboration5.save()
        elaboration6 = Elaboration(challenge=challenge2, user=user1, elaboration_text="test",
                                   submission_time=old)
        elaboration6.save()

        missing_reviews = Elaboration.get_missing_reviews(self.course).values_list('id', flat=True)
        assert dummy_elaboration1.id not in missing_reviews  # is staff
        assert elaboration1.id in missing_reviews  # 2 reviews missing
        assert elaboration2.id in missing_reviews  # 2 reviews missing
        assert elaboration3.id in missing_reviews  # 2 reviews missing
        assert elaboration4.id in missing_reviews  # 2 reviews missing
        assert elaboration5.id in missing_reviews  # 2 reviews missing
        assert elaboration6.id not in missing_reviews  # final challenge

        reviews = []
        reviews.append(Review(elaboration=elaboration1, reviewer=user2, appraisal='S'))
        reviews.append(Review(elaboration=elaboration2, reviewer=user1, appraisal='S'))
        reviews.append(Review(elaboration=elaboration2, reviewer=user3, appraisal='S'))
        reviews.append(Review(elaboration=elaboration3, reviewer=user1, appraisal='S'))
        reviews.append(Review(elaboration=elaboration3, reviewer=user2, appraisal='S'))
        reviews.append(Review(elaboration=elaboration3, reviewer=user4, appraisal='S'))
        reviews.append(Review(elaboration=elaboration4, reviewer=user1, appraisal='S'))
        reviews.append(Review(elaboration=elaboration4, reviewer=user2, appraisal='S'))
        reviews.append(Review(elaboration=elaboration4, reviewer=user3, appraisal='S'))
        reviews.append(Review(elaboration=elaboration4, reviewer=user5, appraisal='S'))
        reviews.append(Review(elaboration=elaboration5, reviewer=user1, appraisal='S'))
        reviews.append(Review(elaboration=elaboration5, reviewer=user2, appraisal='S'))
        reviews.append(Review(elaboration=elaboration5, reviewer=user3, appraisal='S'))
        reviews.append(Review(elaboration=elaboration5, reviewer=user4, appraisal='S'))
        reviews.append(Review(elaboration=elaboration5, reviewer=dummy_user1, appraisal='S'))

        for review in reviews:
            review.save()

        missing_reviews = Elaboration.get_missing_reviews(self.course).values_list('id', flat=True)
        assert dummy_elaboration1 not in missing_reviews  # is staff
        assert elaboration1.id in missing_reviews  # 1 review missing (not submitted)
        assert elaboration2.id in missing_reviews  # 2 reviews missing (not submitted)
        assert elaboration3.id in missing_reviews  # 2 reviews missing (not submitted)
        assert elaboration4.id in missing_reviews  # 2 reviews missing (not submitted)
        assert elaboration5.id in missing_reviews  # 2 reviews missing (not submitted)
        assert elaboration6.id not in missing_reviews  # final challenge

        for review in reviews:
            review.submission_time = old
            review.save()

        assert dummy_elaboration1 not in Elaboration.get_missing_reviews(self.course)  # is staff
        assert elaboration1 in Elaboration.get_missing_reviews(self.course)  # 1 reviews missing
        assert elaboration2 not in Elaboration.get_missing_reviews(self.course)  # 2 reviews
        assert elaboration3 not in Elaboration.get_missing_reviews(self.course)  # 2 reviews
        assert elaboration4 not in Elaboration.get_missing_reviews(self.course)  # 2 reviews
        assert elaboration5 not in Elaboration.get_missing_reviews(self.course)  # 2 reviews
        assert elaboration6 not in Elaboration.get_missing_reviews(self.course)  # final challenge

    def test_get_top_level_tasks(self):
        challenge1 = self.challenge
        self.create_challenge()
        challenge2 = self.challenge
        challenge2.prerequisite = challenge1
        challenge2.save()

        user1 = self.users[0]
        user2 = self.users[1]
        user3 = self.users[2]
        user4 = self.users[3]
        user5 = self.users[4]
        dummy_user1 = self.dummy_users[0]

        dummy_elaboration1 = Elaboration(challenge=challenge1, user=dummy_user1, elaboration_text="test",
                                         submission_time=datetime.now())
        dummy_elaboration1.save()

        elaboration1 = Elaboration(challenge=challenge1, user=user1, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration1.save()
        elaboration2 = Elaboration(challenge=challenge2, user=user1, elaboration_text="test")
        elaboration2.save()
        elaboration3 = Elaboration(challenge=challenge2, user=user2, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration3.save()
        elaboration4 = Elaboration(challenge=challenge2, user=user3, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration4.save()
        elaboration5 = Elaboration(challenge=challenge2, user=dummy_user1, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration5.save()
        elaboration6 = Elaboration(challenge=challenge2, user=user5, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration6.save()

        evaluation1 = Evaluation(submission=elaboration3, tutor=dummy_user1, evaluation_text="test",
                                 evaluation_points=1, submission_time=datetime.now())
        evaluation1.save()
        evaluation2 = Evaluation(submission=elaboration4, tutor=dummy_user1, evaluation_text="test",
                                 evaluation_points=1)
        evaluation2.save()

        assert elaboration1 not in Elaboration.get_top_level_tasks(self.course)  # not a final challenge
        assert elaboration2 not in Elaboration.get_top_level_tasks(self.course)  # elaboration not submitted
        assert elaboration3 not in Elaboration.get_top_level_tasks(self.course)  # already evaluated
        assert elaboration4 in Elaboration.get_top_level_tasks(self.course)  # evaluated but evaluation not submitted
        assert elaboration5 not in Elaboration.get_top_level_tasks(self.course)  # author is staff
        assert elaboration6 in Elaboration.get_top_level_tasks(self.course)  # normal top level

        elaboration2.submission_time = datetime.now()
        elaboration2.save()
        evaluation2.submission_time = datetime.now()
        evaluation2.save()

        assert elaboration1 not in Elaboration.get_top_level_tasks(self.course)  # not a final challenge
        assert elaboration2 in Elaboration.get_top_level_tasks(self.course)  # normal top level
        assert elaboration3 not in Elaboration.get_top_level_tasks(self.course)  # already evaluated
        assert elaboration4 not in Elaboration.get_top_level_tasks(self.course)  # already evaluated
        assert elaboration5 not in Elaboration.get_top_level_tasks(self.course)  # author is staff
        assert elaboration6 in Elaboration.get_top_level_tasks(self.course)  # normal top level

    def test_get_non_adequate_work(self):
        challenge1 = self.challenge
        self.create_challenge()
        challenge2 = self.challenge
        challenge2.prerequisite = challenge1
        challenge2.save()
        user1 = self.users[0]
        user2 = self.users[1]
        user3 = self.users[2]
        user4 = self.users[3]
        user5 = self.users[4]
        dummy_user1 = self.dummy_users[0]

        dummy_elaboration1 = Elaboration(challenge=challenge1, user=dummy_user1, elaboration_text="test_dummy",
                                         submission_time=datetime.now())
        dummy_elaboration1.save()
        elaboration1 = Elaboration(challenge=challenge1, user=user1, elaboration_text="test_1",
                                   submission_time=datetime.now())
        elaboration1.save()
        elaboration2 = Elaboration(challenge=challenge1, user=user2, elaboration_text="test_2",
                                   submission_time=datetime.now())
        elaboration2.save()
        elaboration3 = Elaboration(challenge=challenge1, user=user3, elaboration_text="test_3",
                                   submission_time=datetime.now())
        elaboration3.save()
        elaboration4 = Elaboration(challenge=challenge2, user=user4, elaboration_text="test_4")
        elaboration4.save()
        elaboration5 = Elaboration(challenge=challenge1, user=user5, elaboration_text="test_5",
                                   submission_time=datetime.now())
        elaboration5.save()
        elaboration6 = Elaboration(challenge=challenge1, user=user4, elaboration_text="test_6",
                                   submission_time=datetime.now())
        elaboration6.save()

        assert dummy_elaboration1 not in Elaboration.get_non_adequate_work(self.course)  # author is staff
        assert elaboration1 not in Elaboration.get_non_adequate_work(self.course)  # no reviews yet
        assert elaboration2 not in Elaboration.get_non_adequate_work(self.course)  # no reviews yet
        assert elaboration3 not in Elaboration.get_non_adequate_work(self.course)  # no reviews yet
        assert elaboration4 not in Elaboration.get_non_adequate_work(self.course)  # no reviews yet
        assert elaboration5 not in Elaboration.get_non_adequate_work(self.course)  # no reviews yet
        assert elaboration6 not in Elaboration.get_non_adequate_work(self.course)  # no reviews yet

        review1 = Review(elaboration=elaboration2, reviewer=user3, appraisal='N')
        review1.save()
        Review(elaboration=dummy_elaboration1, reviewer=user2, appraisal='N', submission_time=datetime.now()).save()
        Review(elaboration=elaboration1, reviewer=user2, appraisal='S', submission_time=datetime.now()).save()
        Review(elaboration=elaboration1, reviewer=user3, appraisal='F', submission_time=datetime.now()).save()
        Review(elaboration=elaboration1, reviewer=user4, appraisal='A', submission_time=datetime.now()).save()
        Review(elaboration=elaboration4, reviewer=user1, appraisal='N', submission_time=datetime.now()).save()
        Review(elaboration=elaboration5, reviewer=user1, appraisal='N', submission_time=datetime.now()).save()
        Review(elaboration=elaboration6, reviewer=user1, appraisal='N', submission_time=datetime.now()).save()
        Review(elaboration=elaboration6, reviewer=user2, appraisal='N', submission_time=datetime.now()).save()
        Review(elaboration=elaboration6, reviewer=user3, appraisal='F', submission_time=datetime.now()).save()

        ids = list(elaboration.id for elaboration in Elaboration.get_non_adequate_work(self.course))
        ids.sort()
        assert ids == list(set(ids))  # no duplicates
        assert dummy_elaboration1 not in Elaboration.get_non_adequate_work(self.course)  # author is staff
        assert elaboration1 not in Elaboration.get_non_adequate_work(self.course)  # appraisal not N
        assert elaboration2 not in Elaboration.get_non_adequate_work(self.course)  # review not submitted yet
        assert elaboration3 not in Elaboration.get_non_adequate_work(self.course)  # no reviews yet
        assert elaboration4 not in Elaboration.get_non_adequate_work(self.course)  # final challenge
        assert elaboration5 in Elaboration.get_non_adequate_work(self.course)  # normal non adequate
        assert elaboration6 in Elaboration.get_non_adequate_work(self.course)  # normal non adequate

        review1.submission_time = datetime.now()
        review1.save()
        Review(elaboration=elaboration1, reviewer=user5, appraisal='N', submission_time=datetime.now()).save()
        Review(elaboration=elaboration3, reviewer=user1, appraisal='N', submission_time=datetime.now()).save()

        ids = list(elaboration.id for elaboration in Elaboration.get_non_adequate_work(self.course))
        ids.sort()
        assert ids == list(set(ids))  # no duplicates
        assert dummy_elaboration1 not in Elaboration.get_non_adequate_work(self.course)  # author is staff
        assert elaboration1 in Elaboration.get_non_adequate_work(self.course)  # normal non adequate
        assert elaboration2 in Elaboration.get_non_adequate_work(self.course)  # normal non adequate
        assert elaboration3 in Elaboration.get_non_adequate_work(self.course)  # normal non adequate
        assert elaboration4 not in Elaboration.get_non_adequate_work(self.course)  # final challenge
        assert elaboration5 in Elaboration.get_non_adequate_work(self.course)  # normal non adequate
        assert elaboration6 in Elaboration.get_non_adequate_work(self.course)  # normal non adequate

    def test_get_non_adequate_work2(self):
        challenge1 = self.challenge
        self.create_challenge()
        challenge2 = self.challenge
        challenge2.prerequisite = challenge1
        challenge2.save()
        user1 = self.users[0]
        user2 = self.users[1]
        user3 = self.users[2]
        dummy_user1 = self.dummy_users[0]

        dummy_elaboration1 = Elaboration(challenge=challenge1, user=dummy_user1, elaboration_text="test",
                                         submission_time=datetime.now())
        dummy_elaboration1.save()
        dummy_elaboration2 = Elaboration(challenge=challenge2, user=dummy_user1, elaboration_text="test",
                                         submission_time=datetime.now())
        dummy_elaboration2.save()
        elaboration1 = Elaboration(challenge=challenge1, user=user1, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration1.save()
        elaboration2 = Elaboration(challenge=challenge2, user=user1, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration2.save()
        elaboration3 = Elaboration(challenge=challenge1, user=user2, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration3.save()
        elaboration4 = Elaboration(challenge=challenge2, user=user2, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration4.save()
        elaboration5 = Elaboration(challenge=challenge1, user=user3, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration5.save()
        elaboration6 = Elaboration(challenge=challenge2, user=user3, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration6.save()

        dummy_elaboration1 not in Elaboration.get_non_adequate_work(self.course)  # author staff
        assert elaboration1 not in Elaboration.get_non_adequate_work(self.course)  # no reviews yet
        assert elaboration2 not in Elaboration.get_non_adequate_work(self.course)  # final challenge
        assert elaboration3 not in Elaboration.get_non_adequate_work(self.course)  # no reviews yet
        assert elaboration4 not in Elaboration.get_non_adequate_work(self.course)  # final challenge
        assert elaboration5 not in Elaboration.get_non_adequate_work(self.course)  # no reviews yet
        assert elaboration6 not in Elaboration.get_non_adequate_work(self.course)  # final challenge

        evaluation1 = Evaluation(submission=elaboration4, tutor=dummy_user1, evaluation_text="test",
                                 evaluation_points=1)
        evaluation1.save()
        evaluation2 = Evaluation(submission=elaboration6, tutor=dummy_user1, evaluation_text="test",
                                 evaluation_points=1, submission_time=datetime.now())
        evaluation2.save()

        review1 = Review(elaboration=elaboration1, reviewer=user2, appraisal='N')
        review1.save()
        Review(elaboration=elaboration3, reviewer=user1, appraisal='N', submission_time=datetime.now()).save()
        Review(elaboration=elaboration5, reviewer=user1, appraisal='N', submission_time=datetime.now()).save()

        dummy_elaboration1 not in Elaboration.get_non_adequate_work(self.course)  # author staff
        assert elaboration1 not in Elaboration.get_non_adequate_work(self.course)  # review not submitted
        assert elaboration2 not in Elaboration.get_non_adequate_work(self.course)  # final challenge
        assert elaboration3 in Elaboration.get_non_adequate_work(self.course)  # non adequate
        assert elaboration4 not in Elaboration.get_non_adequate_work(self.course)  # final challenge
        assert elaboration5 not in Elaboration.get_non_adequate_work(self.course)  # final challenge evaluated
        assert elaboration6 not in Elaboration.get_non_adequate_work(self.course)  # final challenge

        evaluation3 = Evaluation(submission=elaboration2, tutor=dummy_user1, evaluation_text="test",
                                 evaluation_points=1, submission_time=datetime.now())
        evaluation3.save()
        evaluation1.submission_time = datetime.now()
        evaluation1.save()

        dummy_elaboration1 not in Elaboration.get_non_adequate_work(self.course)  # author staff
        assert elaboration1 not in Elaboration.get_non_adequate_work(self.course)  # review not submitted
        assert elaboration2 not in Elaboration.get_non_adequate_work(self.course)  # final challenge
        assert elaboration3 not in Elaboration.get_non_adequate_work(self.course)  # final challenge evaluated
        assert elaboration4 not in Elaboration.get_non_adequate_work(self.course)  # final challenge
        assert elaboration5 not in Elaboration.get_non_adequate_work(self.course)  # final challenge evaluated
        assert elaboration6 not in Elaboration.get_non_adequate_work(self.course)  # final challenge

        review1.submission_time = datetime.now()
        review1.save()
        Review(elaboration=elaboration3, reviewer=user3, appraisal='S', submission_time=datetime.now()).save()
        Review(elaboration=elaboration5, reviewer=user2, appraisal='N', submission_time=datetime.now()).save()

        dummy_elaboration1 not in Elaboration.get_non_adequate_work(self.course)  # author staff
        assert elaboration1 not in Elaboration.get_non_adequate_work(self.course)  # final challenge evaluated
        assert elaboration2 not in Elaboration.get_non_adequate_work(self.course)  # final challenge
        assert elaboration3 not in Elaboration.get_non_adequate_work(self.course)  # final challenge evaluated
        assert elaboration4 not in Elaboration.get_non_adequate_work(self.course)  # final challenge
        assert elaboration5 not in Elaboration.get_non_adequate_work(self.course)  # final challenge evaluated
        assert elaboration6 not in Elaboration.get_non_adequate_work(self.course)  # final challenge

        evaluation1.submission_time = None
        evaluation1.save()
        evaluation2.submission_time = None
        evaluation2.save()
        evaluation3.submission_time = None
        evaluation3.save()

        dummy_elaboration1 not in Elaboration.get_non_adequate_work(self.course)  # author staff
        assert elaboration1 in Elaboration.get_non_adequate_work(self.course)  # non adequate
        assert elaboration2 not in Elaboration.get_non_adequate_work(self.course)  # final challenge
        assert elaboration3 in Elaboration.get_non_adequate_work(self.course)  # non adequate
        assert elaboration4 not in Elaboration.get_non_adequate_work(self.course)  # final challenge
        assert elaboration5 in Elaboration.get_non_adequate_work(self.course)  # non adequate
        assert elaboration6 not in Elaboration.get_non_adequate_work(self.course)  # final challenge

    def test_get_evaluated_non_adequate_work(self):
        challenge1 = self.challenge
        self.create_challenge()
        challenge2 = self.challenge
        challenge2.prerequisite = challenge1
        challenge2.save()
        user1 = self.users[0]
        user2 = self.users[1]
        user3 = self.users[2]
        dummy_user1 = self.dummy_users[0]

        dummy_elaboration1 = Elaboration(challenge=challenge1, user=dummy_user1, elaboration_text="test",
                                         submission_time=datetime.now())
        dummy_elaboration1.save()
        dummy_elaboration2 = Elaboration(challenge=challenge2, user=dummy_user1, elaboration_text="test",
                                         submission_time=datetime.now())
        dummy_elaboration2.save()
        elaboration1 = Elaboration(challenge=challenge1, user=user1, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration1.save()
        elaboration2 = Elaboration(challenge=challenge2, user=user1, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration2.save()
        elaboration3 = Elaboration(challenge=challenge1, user=user2, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration3.save()
        elaboration4 = Elaboration(challenge=challenge2, user=user2, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration4.save()
        elaboration5 = Elaboration(challenge=challenge1, user=user3, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration5.save()
        elaboration6 = Elaboration(challenge=challenge2, user=user3, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration6.save()

        dummy_elaboration1 not in Elaboration.get_evaluated_non_adequate_work(self.course)  # author staff
        assert elaboration1 not in Elaboration.get_evaluated_non_adequate_work(self.course)  # no reviews yet
        assert elaboration2 not in Elaboration.get_evaluated_non_adequate_work(self.course)  # final challenge
        assert elaboration3 not in Elaboration.get_evaluated_non_adequate_work(self.course)  # no reviews yet
        assert elaboration4 not in Elaboration.get_evaluated_non_adequate_work(self.course)  # final challenge
        assert elaboration5 not in Elaboration.get_evaluated_non_adequate_work(self.course)  # no reviews yet
        assert elaboration6 not in Elaboration.get_evaluated_non_adequate_work(self.course)  # final challenge

        evaluation1 = Evaluation(submission=elaboration4, tutor=dummy_user1, evaluation_text="test",
                                 evaluation_points=1)
        evaluation1.save()
        evaluation2 = Evaluation(submission=elaboration6, tutor=dummy_user1, evaluation_text="test",
                                 evaluation_points=1, submission_time=datetime.now())
        evaluation2.save()

        review1 = Review(elaboration=elaboration1, reviewer=user2, appraisal='N')
        review1.save()
        Review(elaboration=elaboration3, reviewer=user1, appraisal='N', submission_time=datetime.now()).save()
        Review(elaboration=elaboration5, reviewer=user1, appraisal='N', submission_time=datetime.now()).save()

        dummy_elaboration1 not in Elaboration.get_evaluated_non_adequate_work(self.course)  # author staff
        assert elaboration1 not in Elaboration.get_evaluated_non_adequate_work(self.course)  # no evaluation
        assert elaboration2 not in Elaboration.get_evaluated_non_adequate_work(self.course)  # final challenge
        assert elaboration3 not in Elaboration.get_evaluated_non_adequate_work(self.course)  # evaluation not submitted
        assert elaboration4 not in Elaboration.get_evaluated_non_adequate_work(self.course)  # final challenge
        assert elaboration5 in Elaboration.get_evaluated_non_adequate_work(self.course)  # non adequate
        assert elaboration6 not in Elaboration.get_evaluated_non_adequate_work(self.course)  # final challenge

        Evaluation(submission=elaboration2, tutor=dummy_user1, evaluation_text="test", evaluation_points=1,
                   submission_time=datetime.now()).save()
        evaluation1.submission_time = datetime.now()
        evaluation1.save()

        dummy_elaboration1 not in Elaboration.get_evaluated_non_adequate_work(self.course)  # author staff
        assert elaboration1 not in Elaboration.get_evaluated_non_adequate_work(self.course)  # review not submitted
        assert elaboration2 not in Elaboration.get_evaluated_non_adequate_work(self.course)  # final challenge
        assert elaboration3 in Elaboration.get_evaluated_non_adequate_work(self.course)  # non adequate
        assert elaboration4 not in Elaboration.get_evaluated_non_adequate_work(self.course)  # final challenge
        assert elaboration5 in Elaboration.get_evaluated_non_adequate_work(self.course)  # non adequate
        assert elaboration6 not in Elaboration.get_evaluated_non_adequate_work(self.course)  # final challenge

        review1.submission_time = datetime.now()
        review1.save()
        Review(elaboration=elaboration3, reviewer=user3, appraisal='S', submission_time=datetime.now()).save()
        Review(elaboration=elaboration5, reviewer=user2, appraisal='N', submission_time=datetime.now()).save()

        dummy_elaboration1 not in Elaboration.get_evaluated_non_adequate_work(self.course)  # author staff
        assert elaboration1 in Elaboration.get_evaluated_non_adequate_work(self.course)  # non adequate
        assert elaboration2 not in Elaboration.get_evaluated_non_adequate_work(self.course)  # final challenge
        assert elaboration3 in Elaboration.get_evaluated_non_adequate_work(self.course)  # non adequate
        assert elaboration4 not in Elaboration.get_evaluated_non_adequate_work(self.course)  # final challenge
        assert elaboration5 in Elaboration.get_evaluated_non_adequate_work(self.course)  # non adequate
        assert elaboration6 not in Elaboration.get_evaluated_non_adequate_work(self.course)  # final challenge