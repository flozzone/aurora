"""
Elaboration model method tests
"""

from datetime import datetime
from django.test import TestCase
from PortfolioUser.models import PortfolioUser
from Course.models import Course, CourseUserRelation, CourseChallengeRelation
from Challenge.models import Challenge
from Review.models import Review
from ReviewQuestion.models import ReviewQuestion
from Elaboration.models import Elaboration


class ElaborationTest(TestCase):

    def setUp(self):
        self.create_test_users(4)
        self.create_course()
        self.create_challenge()
        self.create_review_question()
        self.create_elaborations()

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

    def create_test_users(self, amount):
        print("create test users")
        self.users = []
        for i in range(amount):
            self.users.append(self.create_test_user("s%s" % i))

    def create_course(self):
        print("create test course")
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
        print("create test challenge")
        self.challenge = Challenge(
            title='test_title',
            subtitle='test_subtitle',
            description='test_description',
            image_url='test_image_url',
        )
        self.challenge.save()
        CourseChallengeRelation(course=self.course, challenge=self.challenge).save()

    def create_review_question(self):
        print("create test review question")
        self.review_question = ReviewQuestion(
            challenge=self.challenge,
            order=1,
            text="Can you find any additional material not included in this submission?"
        )
        self.review_question.save()

    def create_elaborations(self):
        print("create test elaborations")

        for user in self.users:
            Elaboration(challenge=self.challenge, user=user, elaboration_text="test_text", submission_time=datetime.now()).save()

    def create_review(self, elaboration, reviewer):
        Review(elaboration=elaboration, submission_time=datetime.now(), reviewer=reviewer, appraisal='S').save()

    def test_get_review_candidate_multiple_reviews(self):
        """
        Tests that a review will not be assigned for a an elaboration that has already been reviewed by the reviewer
        """
        for reviewer in self.users:
            elaboration_list=[]
            for _ in range(10):
                elaboration = Elaboration.get_review_candidate(self.challenge, reviewer)
                if elaboration:
                    assert elaboration not in elaboration_list
                    elaboration_list.append(elaboration)
                    print("Candidate - elaboration.id: %s elaboration.user.id: %s reviewer.id: %s" % (elaboration.id, elaboration.user.id, reviewer.id))
                    self.create_review(elaboration, reviewer)

    def test_get_review_candidate_self_review(self):
        """
        Tests that a review will not be assigned for a an elaboration that the reviewer has submitted
        """
        for reviewer in self.users:
            for _ in range(10):
                elaboration = Elaboration.get_review_candidate(self.challenge, reviewer)
                if elaboration:
                    print("Candidate - elaboration.id: %s elaboration.user.id: %s reviewer.id: %s" % (elaboration.id, elaboration.user.id, reviewer.id))
                    assert reviewer.id is not elaboration.user.id
                    self.create_review(elaboration, reviewer)

    def test_get_review_candidate_order(self):
        """
        Tests that the elaboration with the least amount of reviews will be returned
        """
        for reviewer in self.users:
            last_review_amount = 0
            for _ in range(10):
                elaboration = Elaboration.get_review_candidate(self.challenge, reviewer)
                if elaboration:
                    review_amount = Review.get_review_amount(elaboration)
                    assert last_review_amount <= review_amount, "%s should be <= %s" % (last_review_amount, review_amount)
                    last_review_amount = review_amount
                    print("Candidate - elaboration.id: %s elaboration.user.id: %s reviewer.id: %s review_amount: %s" % (elaboration.id, elaboration.user.id, reviewer.id, last_review_amount))
                    self.create_review(elaboration, reviewer)