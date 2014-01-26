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

    AVAILABLE = 0
    PREREQUISITE_MISSING = 1
    USER_REVIEW_MISSING = 2
    WAITING_FOR_SUBMISSION = 3
    BAD_PEER_REVIEW = 4
    PEER_REVIEW_MISSING = 5
    DONE = 6
    WAITING_FOR_EVALUATION = 7
    EVALUATED = 8

    status_dict = {
        0: "Available",
        1: "Prerequisite missing",
        2: "Review missing",
        3: "Waiting for submission",
        4: "Bad Review",
        5: "Waiting for reviews",
        6: "Done",
        7: "Waiting for evaluation",
        8: "Evaluated"
    }

    next_dict = {
        0: "Start the next challenge",
        1: "Prerequisite missing",
        2: "Write another review to proceed",
        3: "Submit your elaboration once it is finished",
        4: "You received a bad review this stack will be blocked until the issue is resolved",
        5: "This submission did not pass the peer review yet",
        6: "Congratulations, this challenge is completed",
        7: "Your submission will be evaluated by a tutor soon",
        8: "Evaluation received this stack is completed"
    }

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

    def is_first_challenge(self):
        return not self.prerequisite # challenge without prerequisite is the first challenge

    def is_final_challenge(self):
        return False if self.get_next() else True

    def get_status_text(self, user):
        status = self.get_status(user)
        status_text = self.status_dict[status]
        next_text = self.next_dict[status]
        return {
            'status': status_text,
            'next': next_text
        }

    def get_status(self, user):
        print("get status for '" + self.title + "':")
        if self.is_first_challenge():  # first challenge is always available
            print("available - because no prerequisite")
        else:
            prerequisite_status = self.prerequisite.get_status(user)
            if not (prerequisite_status is self.DONE or prerequisite_status is self.PEER_REVIEW_MISSING):   # missing prerequisite means unavailable
                print("not available - because prerequisite is not done")
                return self.PREREQUISITE_MISSING

        elaboration = Elaboration.objects.filter(challenge=self, user=user)
        if not elaboration:  # user did all 3 reviews from the prerequisite and therefore start this challenge
            print("available - no elaboration exists yet")
            return self.AVAILABLE
        if not elaboration[0].is_submitted():  # user already wrote an elaboration but did not submit yet
            print("waiting_for_submission - user already wrote an elaboration but did not submit yet")
            return self.WAITING_FOR_SUBMISSION
        if not self.is_final_challenge(): # for normal challenge
            reviews = self.get_reviews_written_by_user(user)
            if not reviews:  # user did not write any reviews yet
                print("user review missing - no review written")
                return self.USER_REVIEW_MISSING
            if len(reviews) < 3:  # user did not write enough reviews yet
                print("user review missing - not enough reviews")
                return self.USER_REVIEW_MISSING
            if not elaboration[0].is_passing_peer_review():
                print("bad_peer_review - unfortunately at least one of the peer reviews was bad")
                return self.BAD_PEER_REVIEW
            if not elaboration[0].is_reviewed_2times():
                print("peer_review_missing - not enough peers wrote a review for this submission")
                return self.PEER_REVIEW_MISSING
            print("done - enough reviews everything is fine")
            return self.DONE
        else:  # for final challenge
            if not elaboration[0].get_evaluation():
                print("waiting_for_evaluation - final challenge is submitted but not yet evaluated by a tutor")
                return self.WAITING_FOR_EVALUATION
            print("evaluated - final challenge is evaluated yay")
            return self.EVALUATED

    def is_enabled_for_user(self, user):
        print("is enabled for user?")
        enabled_for_user = self.get_status(user) != self.PREREQUISITE_MISSING
        print(enabled_for_user)
        print()
        return enabled_for_user

    def is_user_review_missing(self, user):
        print("is user review missing?")
        user_review_missing = self.get_status(user) == self.USER_REVIEW_MISSING
        print(user_review_missing)
        print()
        return

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