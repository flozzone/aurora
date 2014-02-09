"""
Elaboration model method tests
"""

from datetime import datetime
from django.test import TestCase
from PortfolioUser.models import PortfolioUser
from Course.models import Course, CourseUserRelation, CourseChallengeRelation
from Stack.models import Stack, StackChallengeRelation
from Challenge.models import Challenge
from Review.models import Review
from ReviewQuestion.models import ReviewQuestion
from Elaboration.models import Elaboration


class ElaborationTest(TestCase):
    def setUp(self):
        self.create_test_users(4)
        self.create_dummy_users(3)
        self.create_course()
        self.create_stack()
        self.create_challenge()
        self.create_review_question()

    def create_test_user(self, username):
        user = PortfolioUser(username=username)
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
            image_url='test_image_url',
        )
        self.challenge.save()
        CourseChallengeRelation(course=self.course, challenge=self.challenge).save()
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

    def test_get_review_candidate_non_blocked_users(self):
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
        review = Review(elaboration=elaboration1, submission_time=datetime.now(), reviewer=user4,
                        appraisal=Review.SUCCESS)
        review.save()
        assert Elaboration.get_review_candidate(challenge1, user1) == elaboration2  # 2 because 1 is own
        assert Elaboration.get_review_candidate(challenge1, user2) == elaboration1  # 1 because first
        assert Elaboration.get_review_candidate(challenge1, user3) == elaboration1  # 1 because first
        assert Elaboration.get_review_candidate(challenge1, user4) == elaboration2  # 2 because already reviewed for 1
        review.appraisal = Review.FAIL
        review.save()
        assert Elaboration.get_review_candidate(challenge1, user1) == elaboration2  # 2 because 1 is own
        assert Elaboration.get_review_candidate(challenge1, user2) == elaboration1  # 1 because 2 is own
        assert Elaboration.get_review_candidate(challenge1, user3) == elaboration2  # 2 because 1 is blocked
        assert Elaboration.get_review_candidate(challenge1, user4) == elaboration2  # 2 because 1 is blocked
        review.appraisal = Review.NOTHING
        review.save()
        assert Elaboration.get_review_candidate(challenge1, user1) == elaboration2  # 2 because 1 is own
        assert Elaboration.get_review_candidate(challenge1, user2) == elaboration1  # 1 because 2 is own
        assert Elaboration.get_review_candidate(challenge1, user3) == elaboration2  # 2 because 1 is blocked
        assert Elaboration.get_review_candidate(challenge1, user4) == elaboration2  # 2 because 1 is blocked

    def test_get_review_candidate_one_review_missing(self):
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
        Review(elaboration=elaboration4, submission_time=datetime.now(), reviewer=user3,
               appraisal=Review.SUCCESS).save()
        assert Elaboration.get_review_candidate(challenge1, user1) == elaboration4  # 4 because one review missing
        assert Elaboration.get_review_candidate(challenge1, user2) == elaboration4  # 4 because one review missing
        assert Elaboration.get_review_candidate(challenge1, user3) == elaboration1  # 1 because already reviewed for 4
        assert Elaboration.get_review_candidate(challenge1, user4) == elaboration1  # 1 because 4 is own
        Review(elaboration=elaboration3, submission_time=datetime.now(), reviewer=user4,
               appraisal=Review.SUCCESS).save()
        # elaboration 3 has a lower id so it will be first
        assert Elaboration.get_review_candidate(challenge1, user1) == elaboration3  # 3 because one review missing
        assert Elaboration.get_review_candidate(challenge1, user2) == elaboration3  # 3 because one review missing
        assert Elaboration.get_review_candidate(challenge1, user3) == elaboration1  # 1 because already reviewed for 4
        assert Elaboration.get_review_candidate(challenge1, user4) == elaboration1  # 1 because 4 is own

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
        Review(elaboration=elaboration3, submission_time=datetime.now(), reviewer=dummy_user1,
               appraisal=Review.SUCCESS).save()
        Review(elaboration=elaboration4, submission_time=datetime.now(), reviewer=dummy_user1,
               appraisal=Review.SUCCESS).save()
        Review(elaboration=elaboration4, submission_time=datetime.now(), reviewer=dummy_user1,
               appraisal=Review.SUCCESS).save()
        assert Elaboration.get_review_candidate(challenge1, user1) == elaboration3  # 3 because one review is missing
        Review(elaboration=elaboration3, submission_time=datetime.now(), reviewer=dummy_user1,
               appraisal=Review.SUCCESS).save()
        print(Elaboration.get_review_candidate(challenge1, user1).user.username)
        # returns 2 because 2 has 0 reviews and 3 has already enough
        assert Elaboration.get_review_candidate(challenge1, user1) == elaboration2
        Review(elaboration=elaboration2, submission_time=datetime.now(), reviewer=dummy_user1,
               appraisal=Review.SUCCESS).save()
        # should still return 2 because now it has one review missing
        assert Elaboration.get_review_candidate(challenge1, user1) == elaboration2
        Review(elaboration=elaboration2, submission_time=datetime.now(), reviewer=dummy_user1,
               appraisal=Review.SUCCESS).save()
        # should still return 2 because it has the lowest id
        assert Elaboration.get_review_candidate(challenge1, user1) == elaboration2
        Review(elaboration=elaboration2, submission_time=datetime.now(), reviewer=dummy_user1,
               appraisal=Review.SUCCESS).save()
        # should return 3 now because 2 has more reviews and 3 has lower id then 4
        assert Elaboration.get_review_candidate(challenge1, user1) == elaboration3
        Review(elaboration=elaboration3, submission_time=datetime.now(), reviewer=dummy_user1,
               appraisal=Review.SUCCESS).save()
        # should return 4 now because 2 and 3 both have more reviews
        assert Elaboration.get_review_candidate(challenge1, user1) == elaboration4