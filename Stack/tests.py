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


class StackTest(TestCase):
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

    def test_get_challenges(self):
        challenge1 = self.challenge
        assert challenge1 in self.stack.get_challenges()
        self.create_challenge()
        challenge2 = self.challenge
        challenge2.prerequisite = challenge1
        challenge2.save()
        assert challenge1 in self.stack.get_challenges()
        assert challenge2 in self.stack.get_challenges()
        self.create_challenge()
        challenge3 = self.challenge
        challenge3.prerequisite = challenge2
        challenge3.save()
        assert challenge1 in self.stack.get_challenges()
        assert challenge2 in self.stack.get_challenges()
        assert challenge3 in self.stack.get_challenges()

    def test_final_challenge(self):
        challenge1 = self.challenge
        self.create_challenge()
        challenge2 = self.challenge
        challenge2.prerequisite = challenge1
        challenge2.save()
        self.create_challenge()
        challenge3 = self.challenge
        challenge3.prerequisite = challenge2
        challenge3.save()
        assert self.stack.get_final_challenge().id is challenge3.id

    def test_first_challenge(self):
        challenge1 = self.challenge
        self.create_challenge()
        challenge2 = self.challenge
        challenge2.prerequisite = challenge1
        challenge2.save()
        self.create_challenge()
        challenge3 = self.challenge
        challenge3.prerequisite = challenge2
        challenge3.save()
        assert self.stack.get_first_challenge().id is challenge1.id

    def test_is_started(self):
        challenge1 = self.challenge
        self.create_challenge()
        challenge2 = self.challenge
        challenge2.prerequisite = challenge1
        challenge2.save()
        self.create_challenge()
        challenge3 = self.challenge
        challenge3.prerequisite = challenge2
        challenge3.save()
        user = self.users[0]
        elaboration = Elaboration(challenge=challenge1, user=user, elaboration_text="")
        elaboration.save()
        assert self.stack.is_started(user) is False
        elaboration.elaboration_text = "test"
        elaboration.save()
        assert self.stack.is_started(user) is True

    def test_is_evaluated(self):
        user = self.users[0]
        tutor = self.users[1]
        tutor.staff = True
        tutor.save()
        assert self.stack.is_evaluated(user) is False
        elaboration = Elaboration(challenge=self.challenge, user=user, elaboration_text="test elaboration",
                                  submission_time=datetime.now())
        elaboration.save()
        evaluation = Evaluation(submission=elaboration, tutor=tutor, evaluation_text="test_evaluation")
        evaluation.save()
        assert self.stack.is_evaluated(user) is False
        evaluation.submission_time = datetime.now()
        evaluation.evaluation_points = 10
        evaluation.save()
        assert self.stack.is_evaluated(user) is True

    def test_get_points(self):
        user = self.users[0]
        tutor = self.users[1]
        tutor.staff = True
        tutor.save()
        assert self.stack.get_points_earned(user) == 0
        elaboration = Elaboration(challenge=self.challenge, user=user, elaboration_text="test elaboration",
                                  submission_time=datetime.now())
        elaboration.save()
        evaluation = Evaluation(submission=elaboration, tutor=tutor, evaluation_text="test_evaluation",
                                submission_time=datetime.now())
        for points in range(10):
            evaluation.evaluation_points = points
            evaluation.save()
            assert self.stack.get_points_earned(user) == points

    def test_last_available_challenge(self):
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
        assert self.stack.get_last_available_challenge(user1) == challenge1
        Review(elaboration=elaboration2, submission_time=datetime.now(), reviewer=user1,
               appraisal=Review.SUCCESS).save()
        Review(elaboration=elaboration3, submission_time=datetime.now(), reviewer=user1,
               appraisal=Review.SUCCESS).save()
        Review(elaboration=elaboration4, submission_time=datetime.now(), reviewer=user1,
               appraisal=Review.SUCCESS).save()
        assert self.stack.get_last_available_challenge(user1) == challenge2
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
        assert self.stack.get_last_available_challenge(user1) == challenge2
        Review(elaboration=elaboration6, submission_time=datetime.now(), reviewer=user1,
               appraisal=Review.SUCCESS).save()
        Review(elaboration=elaboration7, submission_time=datetime.now(), reviewer=user1,
               appraisal=Review.SUCCESS).save()
        Review(elaboration=elaboration8, submission_time=datetime.now(), reviewer=user1,
               appraisal=Review.SUCCESS).save()
        assert self.stack.get_last_available_challenge(user1) == challenge2
        Review(elaboration=elaboration5, submission_time=datetime.now(), reviewer=user2,
               appraisal=Review.SUCCESS).save()
        Review(elaboration=elaboration5, submission_time=datetime.now(), reviewer=user3,
               appraisal=Review.SUCCESS).save()
        assert self.stack.get_last_available_challenge(user1) == challenge3

    def test_is_blocked(self):
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

        assert not self.stack.is_blocked(user2)
        review = Review(elaboration=elaboration2, submission_time=datetime.now(), reviewer=user1,
                        appraisal=Review.NOTHING)
        review.save()
        assert self.stack.is_blocked(user2)
        review.appraisal = Review.SUCCESS
        review.save()
        assert not self.stack.is_blocked(user2)

        assert not self.stack.is_blocked(user3)
        review = Review(elaboration=elaboration3, submission_time=datetime.now(), reviewer=user1,
                        appraisal=Review.NOTHING)
        review.save()
        assert self.stack.is_blocked(user3)
        review.appraisal = Review.SUCCESS
        review.save()
        assert not self.stack.is_blocked(user3)

        assert not self.stack.is_blocked(user4)
        review = Review(elaboration=elaboration4, submission_time=datetime.now(), reviewer=user1,
                        appraisal=Review.NOTHING)
        review.save()
        assert self.stack.is_blocked(user4)
        review.appraisal = Review.SUCCESS
        review.save()
        assert not self.stack.is_blocked(user4)

        assert not self.stack.is_blocked(user1)
        review = Review(elaboration=elaboration1, submission_time=datetime.now(), reviewer=user2,
                        appraisal=Review.NOTHING)
        review.save()
        assert self.stack.is_blocked(user1)
        review.appraisal = Review.SUCCESS
        review.save()

        assert not self.stack.is_blocked(user1)
        review = Review(elaboration=elaboration1, submission_time=datetime.now(), reviewer=user3,
                        appraisal=Review.NOTHING)
        review.save()
        assert self.stack.is_blocked(user1)
        review.appraisal = Review.SUCCESS
        review.save()
        assert not self.stack.is_blocked(user1)

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

        assert not self.stack.is_blocked(user2)
        review = Review(elaboration=elaboration6, submission_time=datetime.now(), reviewer=user1,
                        appraisal=Review.NOTHING)
        review.save()
        assert self.stack.is_blocked(user2)
        review.appraisal = Review.SUCCESS
        review.save()
        assert not self.stack.is_blocked(user2)

        assert not self.stack.is_blocked(user3)
        review = Review(elaboration=elaboration7, submission_time=datetime.now(), reviewer=user1,
                        appraisal=Review.NOTHING)
        review.save()
        assert self.stack.is_blocked(user3)
        review.appraisal = Review.SUCCESS
        review.save()
        assert not self.stack.is_blocked(user3)

        assert not self.stack.is_blocked(user4)
        review = Review(elaboration=elaboration8, submission_time=datetime.now(), reviewer=user1,
                        appraisal=Review.NOTHING)
        review.save()
        assert self.stack.is_blocked(user4)
        review.appraisal = Review.SUCCESS
        review.save()
        assert not self.stack.is_blocked(user4)

        assert not self.stack.is_blocked(user1)
        review = Review(elaboration=elaboration5, submission_time=datetime.now(), reviewer=user2,
                        appraisal=Review.NOTHING)
        review.save()
        assert self.stack.is_blocked(user1)
        review.appraisal = Review.SUCCESS
        review.save()

        assert not self.stack.is_blocked(user1)
        review = Review(elaboration=elaboration5, submission_time=datetime.now(), reviewer=user3,
                        appraisal=Review.NOTHING)
        review.save()
        assert self.stack.is_blocked(user1)
        review.appraisal = Review.SUCCESS
        review.save()
        assert not self.stack.is_blocked(user1)

    def test_has_enough_peer_reviews(self):
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

        assert not self.stack.has_enough_peer_reviews(user1)
        Review(elaboration=elaboration1, submission_time=datetime.now(), reviewer=user2,
               appraisal=Review.SUCCESS).save()
        assert not self.stack.has_enough_peer_reviews(user1)
        Review(elaboration=elaboration1, submission_time=datetime.now(), reviewer=user3,
               appraisal=Review.SUCCESS).save()
        assert not self.stack.has_enough_peer_reviews(user1)

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

        Review(elaboration=elaboration6, submission_time=datetime.now(), reviewer=user1,
               appraisal=Review.SUCCESS).save()
        Review(elaboration=elaboration7, submission_time=datetime.now(), reviewer=user1,
               appraisal=Review.SUCCESS).save()
        Review(elaboration=elaboration8, submission_time=datetime.now(), reviewer=user1,
               appraisal=Review.SUCCESS).save()

        assert not self.stack.has_enough_peer_reviews(user1)
        Review(elaboration=elaboration5, submission_time=datetime.now(), reviewer=user2,
               appraisal=Review.SUCCESS).save()
        assert not self.stack.has_enough_peer_reviews(user1)
        Review(elaboration=elaboration5, submission_time=datetime.now(), reviewer=user3,
               appraisal=Review.SUCCESS).save()
        assert self.stack.has_enough_peer_reviews(user1)
