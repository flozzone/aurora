from datetime import datetime
from django.test import TestCase

from AuroraUser.models import AuroraUser
from Course.models import Course, CourseUserRelation
from Challenge.models import Challenge
from Review.models import Review, ReviewConfig
from ReviewQuestion.models import ReviewQuestion
from Elaboration.models import Elaboration
from Stack.models import Stack, StackChallengeRelation


class SimpleTest(TestCase):
    def setUp(self):
        self.create_test_users(4)
        self.create_course()
        self.create_challenge()
        self.create_review_question()
        self.create_elaborations()

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

    def create_challenge(self):
        self.challenge = Challenge(
            title='test_title',
            subtitle='test_subtitle',
            description='test_description',
            course=self.course,
        )
        self.challenge.save()

    def create_review_question(self):
        self.review_question = ReviewQuestion(
            challenge=self.challenge,
            order=1,
            text="Can you find any additional material not included in this submission?"
        )
        self.review_question.save()

    def create_elaborations(self):
        self.elaborations = []
        for user in self.users:
            elaboration = Elaboration(challenge=self.challenge, user=user, elaboration_text="test_text",
                                      submission_time=datetime.now())
            elaboration.save()
            self.elaborations.append(elaboration)

    def create_review_without_submission_date(self, elaboration, reviewer):
        Review(elaboration=elaboration, reviewer=reviewer, appraisal='S').save()

    def create_review(self, elaboration, reviewer):
        Review(elaboration=elaboration, reviewer=reviewer, submission_time=datetime.now(), appraisal='S').save()

    def test_get_open_review(self):
        user1 = self.users[0]
        user2 = self.users[2]
        elaboration = self.elaborations[0]
        self.create_review_without_submission_date(elaboration=elaboration, reviewer=user1)

        # there should be an open review for user1
        review = Review.get_open_review(self.challenge, user1)
        assert review
        assert review.reviewer == user1
        assert review.elaboration == elaboration

        # there should be no open review for user1 since the review is already submitted
        review.submission_time = datetime.now()
        review.save()
        review = Review.get_open_review(self.challenge, user1)
        assert not review

        # there should be no open review for user2
        review = Review.get_open_review(self.challenge, user2)
        assert not review

        # user1 and user2 both have separate open reviews
        self.create_review_without_submission_date(elaboration=elaboration, reviewer=user1)
        self.create_review_without_submission_date(elaboration=elaboration, reviewer=user2)
        review1 = Review.get_open_review(self.challenge, user1)
        review2 = Review.get_open_review(self.challenge, user2)
        assert review1
        assert review2
        assert review1.id != review2.id
        assert review1.reviewer == user1
        assert review2.reviewer == user2
        assert review1.elaboration == elaboration and review2.elaboration == elaboration

    def test_review_config_offset(self):
        assert ReviewConfig.get_candidate_offset_min() == 0
        assert ReviewConfig.get_candidate_offset_max() == 0
        ReviewConfig(candidate_offset_min=1, candidate_offset_max=2).save()
        assert ReviewConfig.get_candidate_offset_min() == 1
        assert ReviewConfig.get_candidate_offset_max() == 2

    def test_notification_too_soon(self):
        challenge1 = self.challenge
        challenge2 = Challenge(
            course=self.course,
            prerequisite=challenge1,
        )
        challenge2.save()

        challenge3 = Challenge(
            course=self.course,
            prerequisite=challenge2,
        )
        challenge3.save()
        stack = Stack(course=self.course)
        stack.save()
        StackChallengeRelation(stack=stack, challenge=challenge1).save()
        StackChallengeRelation(stack=stack, challenge=challenge2).save()
        StackChallengeRelation(stack=stack, challenge=challenge3).save()
        elab1 = challenge1.get_elaboration(self.users[0])
        elab2 = Elaboration(challenge=challenge2, user=self.users[0])
        elab2.save()
        assert stack.has_enough_peer_reviews(self.users[0]) is False
        Review(elaboration=elab2, reviewer=self.users[1], appraisal='S', submission_time=datetime.now()).save()
        Review(elaboration=elab2, reviewer=self.users[2], appraisal='S', submission_time=datetime.now()).save()
        assert stack.has_enough_peer_reviews(self.users[0]) is False
        Review(elaboration=elab1, reviewer=self.users[1], appraisal='S', submission_time=datetime.now()).save()
        Review(elaboration=elab1, reviewer=self.users[2], appraisal='S', submission_time=datetime.now()).save()
        assert stack.has_enough_peer_reviews(self.users[0]) is True