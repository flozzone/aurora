from django.db import models
from Stack.models import StackChallengeRelation
from ReviewQuestion.models import ReviewQuestion
from Review.models import Review
from Elaboration.models import Elaboration


class Challenge(models.Model):
    reviews_per_challenge = 3

    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=100)
    prerequisite = models.ForeignKey('self', null=True)
    description = models.TextField()
    image_url = models.CharField(max_length=100)
    # This is a comma separated list of mime types or file extensions. Eg.: image/*,application/pdf,.psd.
    accepted_files = models.CharField(max_length=100, default="image/*,application/pdf")

    AVAILABLE = 'available'
    NOT_AVAILABLE = 'not_available'
    REVIEW_MISSING = 'review_missing'

    def get_previous(self):
        return self.prerequisite

    def get_next(self):  # TODO: this will not work if we branch out stacks (can return multiple results)
        next_challenges = Challenge.objects.filter(prerequisite=self)
        if next_challenges:
            return next_challenges[0]
        else:
            return None

    def get_stack(self):
        stack_challenge_relation = StackChallengeRelation.objects.filter(challenge=self)
        if stack_challenge_relation:
            return stack_challenge_relation[0].stack    # TODO: does not work with challenge in multiple stacks
        else:
            return None

    def is_final_challenge(self):
        return False if self.get_next() else True

    def get_status(self, user):
        if not self.prerequisite:  # challenge has no prerequisite
            return self.AVAILABLE
        if not self.prerequisite.submitted_by_user(user):
            return self.NOT_AVAILABLE
        reviews = self.prerequisite.get_reviews_written_by_user(user)
        if not reviews:  # user did not write any reviews yet
            return self.REVIEW_MISSING
        if len(reviews) < 3:  # user did not write enough reviews yet
            return self.REVIEW_MISSING
        return self.AVAILABLE

    def is_available_for_user(self, user):
        return self.get_status(user) == self.AVAILABLE

    def is_review_missing(self, user):
        print(self.get_status(user))
        return self.get_status(user) == self.REVIEW_MISSING

    def submitted_by_user(self, user):
        elaboration = Elaboration.objects.filter(challenge=self, user=user)
        if not elaboration:  # no elaboration for this user for this challenge
            return False
        return elaboration[0].is_submitted()

    def get_reviews_written_by_user(self, user):
        reviews = []
        for review in Review.objects.filter(elaboration__challenge=self, reviewer=user):
            reviews.append(review)
        return reviews

    def get_peer_review_questions(self):
        peer_review_questions = []
        for peer_review_question in ReviewQuestion.objects.filter(challenge=self).order_by('order'):
            peer_review_questions.append(peer_review_question)
        return peer_review_questions

    def get_submissions(self):
        submissions = Elaboration.objects.filter(challenge=self)
        return submissions