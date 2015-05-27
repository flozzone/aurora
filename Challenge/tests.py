"""
Challenge model method tests
"""

from datetime import datetime

from django.test import TestCase

from AuroraUser.models import AuroraUser
from Stack.models import Stack, StackChallengeRelation
from Course.models import Course, CourseUserRelation
from Challenge.models import Challenge
from ReviewQuestion.models import ReviewQuestion
from Elaboration.models import Elaboration
from Evaluation.models import Evaluation
from Review.models import Review


class ChallengeTest(TestCase):
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

    def test_next(self):
        challenge1 = self.challenge
        self.create_challenge()
        challenge2 = self.challenge
        challenge2.prerequisite = challenge1
        challenge2.save()
        self.create_challenge()
        challenge3 = self.challenge
        challenge3.prerequisite = challenge2
        challenge3.save()
        assert challenge1.get_next() == challenge2
        assert challenge2.get_next() == challenge3
        assert challenge3.get_next() is None

    def test_get_elaboration(self):
        user = self.users[0]
        assert self.challenge.get_elaboration(user) is None
        elaboration = Elaboration(challenge=self.challenge, user=user, elaboration_text="test")
        elaboration.save()
        assert self.challenge.get_elaboration(user) == elaboration

    def test_get_stack(self):
        challenge = Challenge(
            title='test_title',
            subtitle='test_subtitle',
            description='test_description',
            course=self.course
        )
        challenge.save()
        assert challenge.get_stack() is None
        assert self.challenge.get_stack() == self.stack

    def test_is_first_challenge(self):
        challenge1 = self.challenge
        self.create_challenge()
        challenge2 = self.challenge
        challenge2.prerequisite = challenge1
        challenge2.save()
        self.create_challenge()
        challenge3 = self.challenge
        challenge3.prerequisite = challenge2
        challenge3.save()
        assert challenge1.is_first_challenge()
        assert not challenge2.is_first_challenge()
        assert not challenge3.is_first_challenge()

    def test_is_final_challenge(self):
        challenge1 = self.challenge
        self.create_challenge()
        challenge2 = self.challenge
        challenge2.prerequisite = challenge1
        challenge2.save()
        self.create_challenge()
        challenge3 = self.challenge
        challenge3.prerequisite = challenge2
        challenge3.save()
        assert not challenge1.is_final_challenge()
        assert not challenge2.is_final_challenge()
        assert challenge3.is_final_challenge()

    def test_get_final_challenge(self):
        challenge1 = self.challenge
        self.create_challenge()
        challenge2 = self.challenge
        challenge2.prerequisite = challenge1
        challenge2.save()
        self.create_challenge()
        challenge3 = self.challenge
        challenge3.prerequisite = challenge2
        challenge3.save()
        assert challenge1.get_final_challenge() == challenge3
        assert challenge2.get_final_challenge() == challenge3
        assert challenge3.get_final_challenge() == challenge3

    def test_get_first_challenge(self):
        challenge1 = self.challenge
        self.create_challenge()
        challenge2 = self.challenge
        challenge2.prerequisite = challenge1
        challenge2.save()
        self.create_challenge()
        challenge3 = self.challenge
        challenge3.prerequisite = challenge2
        challenge3.save()
        assert challenge1.get_first_challenge() == challenge1
        assert challenge2.get_first_challenge() == challenge1
        assert challenge3.get_first_challenge() == challenge1

    def test_has_enough_user_reviews(self):
        challenge1 = self.challenge
        self.create_challenge()
        challenge2 = self.challenge
        challenge2.prerequisite = challenge1
        challenge2.save()
        user1 = self.users[0]
        elaboration1 = Elaboration(challenge=challenge1, user=user1, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration1.save()
        user2 = self.users[1]
        elaboration2 = Elaboration(challenge=challenge1, user=user2, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration2.save()
        user3 = self.users[2]
        elaboration3 = Elaboration(challenge=challenge1, user=user3, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration3.save()
        user4 = self.users[3]
        elaboration4 = Elaboration(challenge=challenge1, user=user4, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration4.save()
        assert not challenge1.has_enough_user_reviews(user1)
        Review(elaboration=elaboration2, submission_time=datetime.now(), reviewer=user1,
               appraisal=Review.SUCCESS).save()
        assert not challenge1.has_enough_user_reviews(user1)
        Review(elaboration=elaboration3, submission_time=datetime.now(), reviewer=user1,
               appraisal=Review.SUCCESS).save()
        assert not challenge1.has_enough_user_reviews(user1)
        Review(elaboration=elaboration4, submission_time=datetime.now(), reviewer=user1,
               appraisal=Review.SUCCESS).save()
        assert challenge1.has_enough_user_reviews(user1)

    def test_is_started(self):
        user = self.users[0]
        elaboration = Elaboration(challenge=self.challenge, user=user, elaboration_text="")
        elaboration.save()
        assert self.challenge.is_started(user) is False
        elaboration.elaboration_text="test"
        elaboration.save()
        assert self.challenge.is_started(user) is True

    def test_submitted_by_user(self):
        user = self.users[0]
        elaboration = Elaboration(challenge=self.challenge, user=user, elaboration_text="test")
        elaboration.save()
        assert not self.challenge.submitted_by_user(user)
        elaboration.submission_time = datetime.now()
        elaboration.save()
        assert self.challenge.submitted_by_user(user)

    def test_get_review_written_by_user(self):
        challenge1 = self.challenge
        self.create_challenge()
        challenge2 = self.challenge
        challenge2.prerequisite = challenge1
        challenge2.save()
        user1 = self.users[0]
        elaboration1 = Elaboration(challenge=challenge1, user=user1, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration1.save()
        user2 = self.users[1]
        elaboration2 = Elaboration(challenge=challenge1, user=user2, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration2.save()
        user3 = self.users[2]
        elaboration3 = Elaboration(challenge=challenge1, user=user3, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration3.save()
        user4 = self.users[3]
        elaboration4 = Elaboration(challenge=challenge1, user=user4, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration4.save()
        assert len(challenge1.get_reviews_written_by_user(user1)) == 0
        review1 = Review(elaboration=elaboration2, submission_time=datetime.now(), reviewer=user1,
                         appraisal=Review.SUCCESS)
        review1.save()
        assert len(challenge1.get_reviews_written_by_user(user1)) == 1
        assert review1 in challenge1.get_reviews_written_by_user(user1)
        review2 = Review(elaboration=elaboration3, submission_time=datetime.now(), reviewer=user1,
                         appraisal=Review.SUCCESS)
        review2.save()
        assert len(challenge1.get_reviews_written_by_user(user1)) == 2
        assert review1 in challenge1.get_reviews_written_by_user(user1)
        assert review2 in challenge1.get_reviews_written_by_user(user1)
        review3 = Review(elaboration=elaboration4, submission_time=datetime.now(), reviewer=user1,
                         appraisal=Review.SUCCESS)
        review3.save()
        assert len(challenge1.get_reviews_written_by_user(user1)) == 3
        assert review1 in challenge1.get_reviews_written_by_user(user1)
        assert review2 in challenge1.get_reviews_written_by_user(user1)
        assert review3 in challenge1.get_reviews_written_by_user(user1)

    def test_get_elaborations(self):
        assert len(self.challenge.get_elaborations()) == 0
        user = self.users[0]
        elaboration = Elaboration(challenge=self.challenge, user=user, elaboration_text="test")
        elaboration.save()
        assert len(self.challenge.get_elaborations()) == 1
        assert elaboration in self.challenge.get_elaborations()

    def test_first_challenge_is_always_enabled(self):
        user = self.users[0]
        assert self.challenge.is_enabled_for_user(user)

    def test_already_submitted_challenges_are_enabled(self):
        challenge1 = self.challenge
        self.create_challenge()
        challenge2 = self.challenge
        challenge2.prerequisite = challenge1
        challenge2.save()
        user = self.users[0]
        assert not challenge2.is_enabled_for_user(user)
        elaboration = Elaboration(challenge=challenge2, user=user, elaboration_text="test")
        elaboration.save()
        assert not challenge2.is_enabled_for_user(user)
        elaboration.submission_time = datetime.now()
        elaboration.save()
        assert challenge2.is_enabled_for_user(user)

    def test_enough_user_reviews_required(self):
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
        assert not challenge2.is_enabled_for_user(user1)
        Review(elaboration=elaboration2, submission_time=datetime.now(), reviewer=user1,
               appraisal=Review.SUCCESS).save()
        assert not challenge2.is_enabled_for_user(user1)
        Review(elaboration=elaboration3, submission_time=datetime.now(), reviewer=user1,
               appraisal=Review.SUCCESS).save()
        assert not challenge2.is_enabled_for_user(user1)
        Review(elaboration=elaboration4, submission_time=datetime.now(), reviewer=user1,
               appraisal=Review.SUCCESS).save()
        assert challenge2.is_enabled_for_user(user1)

    def test_if_stack_blocked_challenge_is_not_enabled_fail(self):
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
        Review(elaboration=elaboration2, submission_time=datetime.now(), reviewer=user1,
               appraisal=Review.SUCCESS).save()
        Review(elaboration=elaboration3, submission_time=datetime.now(), reviewer=user1,
               appraisal=Review.SUCCESS).save()
        Review(elaboration=elaboration4, submission_time=datetime.now(), reviewer=user1,
               appraisal=Review.SUCCESS).save()
        assert challenge2.is_enabled_for_user(user1)
        Review(elaboration=elaboration1, submission_time=datetime.now(), reviewer=user2, appraisal=Review.FAIL).save()
        # a failed review does not block the stack
        assert challenge2.is_enabled_for_user(user1)

    def test_if_stack_blocked_challenge_is_not_enabled_nothing(self):
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
        Review(elaboration=elaboration2, submission_time=datetime.now(), reviewer=user1,
               appraisal=Review.SUCCESS).save()
        Review(elaboration=elaboration3, submission_time=datetime.now(), reviewer=user1,
               appraisal=Review.SUCCESS).save()
        Review(elaboration=elaboration4, submission_time=datetime.now(), reviewer=user1,
               appraisal=Review.SUCCESS).save()
        assert challenge2.is_enabled_for_user(user1)
        Review(elaboration=elaboration1, submission_time=datetime.now(), reviewer=user2,
               appraisal=Review.NOTHING).save()
        # nothing should not block a user from working
        assert challenge2.is_enabled_for_user(user1)

    def test_final_challenge_enabled(self):
        challenge1 = self.challenge
        self.create_challenge()
        challenge2 = self.challenge
        challenge2.prerequisite = challenge1
        challenge2.save()
        user1 = self.users[0]
        user2 = self.users[1]
        user3 = self.users[2]
        user4 = self.users[3]
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
        Review(elaboration=elaboration2, submission_time=datetime.now(), reviewer=user1,
               appraisal=Review.SUCCESS).save()
        Review(elaboration=elaboration3, submission_time=datetime.now(), reviewer=user1,
               appraisal=Review.SUCCESS).save()
        Review(elaboration=elaboration4, submission_time=datetime.now(), reviewer=user1,
               appraisal=Review.SUCCESS).save()
        assert not challenge2.is_enabled_for_user(user1)
        Review(elaboration=elaboration1, submission_time=datetime.now(), reviewer=user2,
               appraisal=Review.SUCCESS).save()
        Review(elaboration=elaboration1, submission_time=datetime.now(), reviewer=user3,
               appraisal=Review.SUCCESS).save()
        assert challenge2.is_enabled_for_user(user1)

    def test_final_challenge_enabled_bug_issue_114(self):
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
        Review(elaboration=elaboration2, submission_time=datetime.now(), reviewer=user1,
               appraisal=Review.SUCCESS).save()
        Review(elaboration=elaboration3, submission_time=datetime.now(), reviewer=user1,
               appraisal=Review.SUCCESS).save()
        Review(elaboration=elaboration4, submission_time=datetime.now(), reviewer=user1,
               appraisal=Review.SUCCESS).save()
        assert not challenge3.is_enabled_for_user(user1)
        Review(elaboration=elaboration1, submission_time=datetime.now(), reviewer=user2,
               appraisal=Review.SUCCESS).save()
        Review(elaboration=elaboration1, submission_time=datetime.now(), reviewer=user3,
               appraisal=Review.SUCCESS).save()

        assert not challenge3.is_enabled_for_user(user1)

    def test_status_not_started(self):
        user = self.users[0]
        assert self.challenge.is_enabled_for_user(user)
        assert self.challenge.get_status(user) == Challenge.NOT_STARTED

    def test_status_not_submitted(self):
        challenge1 = self.challenge
        self.create_challenge()
        challenge2 = self.challenge
        challenge2.prerequisite = challenge1
        challenge2.save()
        user = self.users[0]
        assert challenge1.get_status(user) == Challenge.NOT_STARTED
        elaboration = Elaboration(challenge=challenge1, user=user, elaboration_text="test")
        elaboration.save()
        assert challenge1.is_enabled_for_user(user)
        assert challenge1.get_status(user) == Challenge.NOT_SUBMITTED
        assert not challenge2.is_enabled_for_user(user)
        assert challenge2.get_status(user) == Challenge.NOT_ENABLED

    def test_status_blocked_bad_review_fail(self):
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
        assert not challenge2.is_enabled_for_user(user1)
        assert challenge1.get_status(user1) == Challenge.USER_REVIEW_MISSING
        assert challenge2.get_status(user1) == Challenge.NOT_ENABLED
        bad_review = Review(elaboration=elaboration1, submission_time=datetime.now(), reviewer=user2,
                            appraisal=Review.FAIL)
        bad_review.save()
        assert not challenge2.is_enabled_for_user(user1)
        assert challenge1.get_status(user1) == Challenge.USER_REVIEW_MISSING
        assert challenge2.get_status(user1) == Challenge.NOT_ENABLED
        bad_review.appraisal = Review.SUCCESS
        bad_review.save()
        Review(elaboration=elaboration2, submission_time=datetime.now(), reviewer=user1,
               appraisal=Review.SUCCESS).save()
        Review(elaboration=elaboration3, submission_time=datetime.now(), reviewer=user1,
               appraisal=Review.SUCCESS).save()
        Review(elaboration=elaboration4, submission_time=datetime.now(), reviewer=user1,
               appraisal=Review.SUCCESS).save()
        assert challenge1.has_enough_user_reviews(user1)
        assert challenge1.get_status(user1) == Challenge.DONE_MISSING_PEER_REVIEW

        assert challenge2.is_enabled_for_user(user1)
        assert challenge2.get_status(user1) == Challenge.NOT_STARTED
        bad_review.appraisal = Review.FAIL
        bad_review.save()
        assert challenge2.is_enabled_for_user(user1)
        assert challenge2.get_status(user1) == Challenge.NOT_STARTED

    def test_status_blocked_bad_review_nothing(self):
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
        assert not challenge2.is_enabled_for_user(user1)
        assert challenge1.get_status(user1) == Challenge.USER_REVIEW_MISSING
        assert challenge2.get_status(user1) == Challenge.NOT_ENABLED
        bad_review = Review(elaboration=elaboration1, submission_time=datetime.now(), reviewer=user2,
                            appraisal=Review.NOTHING)
        bad_review.save()
        assert not challenge2.is_enabled_for_user(user1)
        assert challenge1.get_status(user1) == Challenge.BLOCKED_BAD_REVIEW
        assert challenge2.get_status(user1) == Challenge.NOT_ENABLED
        bad_review.appraisal = Review.SUCCESS
        bad_review.save()
        Review(elaboration=elaboration2, submission_time=datetime.now(), reviewer=user1,
               appraisal=Review.SUCCESS).save()
        Review(elaboration=elaboration3, submission_time=datetime.now(), reviewer=user1,
               appraisal=Review.SUCCESS).save()
        Review(elaboration=elaboration4, submission_time=datetime.now(), reviewer=user1,
               appraisal=Review.SUCCESS).save()
        assert challenge1.has_enough_user_reviews(user1)
        assert challenge1.get_status(user1) == Challenge.DONE_MISSING_PEER_REVIEW

        assert challenge2.is_enabled_for_user(user1)
        assert challenge2.get_status(user1) == Challenge.NOT_STARTED
        bad_review.appraisal = Review.NOTHING
        bad_review.save()
        assert challenge2.is_enabled_for_user(user1)
        assert challenge2.get_status(user1) == Challenge.NOT_STARTED

    def test_status_user_review_missing(self):
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
        assert challenge1.is_enabled_for_user(user1)
        assert challenge1.get_status(user1) == Challenge.USER_REVIEW_MISSING
        assert not challenge2.is_enabled_for_user(user1)
        assert challenge2.get_status(user1) == Challenge.NOT_ENABLED
        Review(elaboration=elaboration2, submission_time=datetime.now(), reviewer=user1,
               appraisal=Review.SUCCESS).save()
        assert challenge1.is_enabled_for_user(user1)
        assert challenge1.get_status(user1) == Challenge.USER_REVIEW_MISSING
        assert not challenge2.is_enabled_for_user(user1)
        assert challenge2.get_status(user1) == Challenge.NOT_ENABLED
        Review(elaboration=elaboration3, submission_time=datetime.now(), reviewer=user1,
               appraisal=Review.SUCCESS).save()
        assert challenge1.is_enabled_for_user(user1)
        assert challenge1.get_status(user1) == Challenge.USER_REVIEW_MISSING
        assert not challenge2.is_enabled_for_user(user1)
        assert challenge2.get_status(user1) == Challenge.NOT_ENABLED
        Review(elaboration=elaboration4, submission_time=datetime.now(), reviewer=user1,
               appraisal=Review.SUCCESS).save()
        assert challenge1.is_enabled_for_user(user1)
        assert challenge1.get_status(user1) == Challenge.DONE_MISSING_PEER_REVIEW
        assert challenge2.is_enabled_for_user(user1)
        assert challenge2.get_status(user1) == Challenge.NOT_STARTED

    def test_status_done_missing_peer_review(self):
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
        Review(elaboration=elaboration2, submission_time=datetime.now(), reviewer=user1,
               appraisal=Review.SUCCESS).save()
        Review(elaboration=elaboration3, submission_time=datetime.now(), reviewer=user1,
               appraisal=Review.SUCCESS).save()
        Review(elaboration=elaboration4, submission_time=datetime.now(), reviewer=user1,
               appraisal=Review.SUCCESS).save()
        assert challenge1.get_status(user1) == Challenge.DONE_MISSING_PEER_REVIEW
        Review(elaboration=elaboration1, submission_time=datetime.now(), reviewer=user2,
               appraisal=Review.SUCCESS).save()
        assert challenge1.get_status(user1) == Challenge.DONE_MISSING_PEER_REVIEW
        Review(elaboration=elaboration1, submission_time=datetime.now(), reviewer=user3,
               appraisal=Review.SUCCESS).save()
        assert challenge1.get_status(user1) == Challenge.DONE_MISSING_PEER_REVIEW

    def test_status_final_challenge(self):
        challenge1 = self.challenge
        self.create_challenge()
        challenge2 = self.challenge
        challenge2.prerequisite = challenge1
        challenge2.save()
        user1 = self.users[0]
        elaboration1 = Elaboration(challenge=challenge1, user=user1, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration1.save()
        user2 = self.users[1]
        elaboration2 = Elaboration(challenge=challenge1, user=user2, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration2.save()
        user3 = self.users[2]
        elaboration3 = Elaboration(challenge=challenge1, user=user3, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration3.save()
        user4 = self.users[3]
        elaboration4 = Elaboration(challenge=challenge1, user=user4, elaboration_text="test",
                                   submission_time=datetime.now())
        elaboration4.save()
        Review(elaboration=elaboration2, submission_time=datetime.now(), reviewer=user1,
               appraisal=Review.SUCCESS).save()
        Review(elaboration=elaboration3, submission_time=datetime.now(), reviewer=user1,
               appraisal=Review.SUCCESS).save()
        Review(elaboration=elaboration4, submission_time=datetime.now(), reviewer=user1,
               appraisal=Review.SUCCESS).save()
        assert challenge1.get_status(user1) == Challenge.DONE_MISSING_PEER_REVIEW
        assert challenge2.get_status(user1) == Challenge.NOT_ENABLED
        Review(elaboration=elaboration1, submission_time=datetime.now(), reviewer=user2,
               appraisal=Review.SUCCESS).save()
        Review(elaboration=elaboration1, submission_time=datetime.now(), reviewer=user3,
               appraisal=Review.SUCCESS).save()
        assert challenge1.get_status(user1) == Challenge.DONE_PEER_REVIEWED
        assert challenge2.get_status(user1) == Challenge.NOT_STARTED
        final_elaboration = Elaboration(challenge=challenge2, user=user1, elaboration_text="test",
                                        submission_time=datetime.now())
        final_elaboration.save()
        assert challenge2.get_status(user1) == Challenge.WAITING_FOR_EVALUATION
        tutor = user4
        tutor.staff = True
        tutor.save()
        Evaluation(submission=final_elaboration, tutor=tutor, evaluation_text="test evaluation", evaluation_points=10,
                   submission_time=datetime.now()).save()
        assert challenge2.get_status(user1) == Challenge.EVALUATED


