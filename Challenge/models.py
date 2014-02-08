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

    NOT_ENABLED = -1
    NOT_STARTED = 0
    NOT_SUBMITTED = 1
    USER_REVIEW_MISSING = 2
    BLOCKED_BAD_REVIEW = 3
    DONE_MISSING_PEER_REVIEW = 4
    DONE_PEER_REVIEWED = 5
    WAITING_FOR_EVALUATION = 6
    EVALUATED = 7

    status_dict = {
        -1: "Not enabled",
        0: "Not started",
        1: "Not submitted",
        2: "Review missing",
        3: "Bad review",
        4: "Done, missing peer review", # can proceed but will be a problem for final challenge
        5: "Done, peer reviewed",
        6: "Waiting for evaluation",
        7: "Evaluated"
    }

    next_dict = {
        -1: "Not enabled",
        0: "Start the next challenge",
        1: "Submit your elaboration once it is finished",
        2: "Write another review to proceed",
        3: "You received a bad review this stack will be blocked until the issue is resolved",
        4: "Done. This submission did not pass the peer review yet (needed to enable final challenge)",
        5: "Congratulations, this challenge passed all peer reviews",
        6: "Your submission will be evaluated by a tutor soon",
        7: "Evaluation received this stack is completed"
    }

    def get_next(self):
        next_challenges = Challenge.objects.filter(prerequisite=self)
        if next_challenges:
            return next_challenges[0]
        else:
            return None

    def get_elaboration(self, user):
        try:
            return Elaboration.objects.get(challenge=self, user=user)
        except Elaboration.DoesNotExist:
            return None

    def get_stack(self):
        stack_challenge_relation = StackChallengeRelation.objects.filter(challenge=self)
        if stack_challenge_relation:
            return stack_challenge_relation[0].stack
        else:
            return None

    def is_first_challenge(self):
        return not self.prerequisite  # challenge without prerequisite is the first challenge

    def is_final_challenge(self):
        return False if self.get_next() else True

    def get_final_challenge(self):
        next_challenge = self
        while not next_challenge.is_final_challenge():
            next_challenge = next_challenge.get_next()
        return next_challenge

    def has_enough_user_reviews(self, user):
        return len(self.get_reviews_written_by_user(user)) >= 3

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

    def get_elaborations(self):
        submissions = Elaboration.objects.filter(challenge=self)
        return submissions

    def get_status_text(self, user):
        status = self.get_status(user)
        status_text = self.status_dict[status]
        next_text = self.next_dict[status]
        return {
            'status': status_text,
            'next': next_text
        }

    def is_enabled_for_user(self, user):
        # first challenge is always enabled
        if self.is_first_challenge():
            print("is first challenge")
            return True

        # if challenge is already submitted it is enabled by default
        elaboration = self.get_elaboration(user)
        if elaboration:
            print("has elaboration")
            if elaboration.is_submitted():
                print("elaboration is submitted")
                return True

        # if the stack is blocked the challenge is not available
        if self.get_stack().is_blocked(user):
            print("stack is blocked")
            return False

        # if not final challenge the prerequisite must have enough (3) user reviews
        if not self.is_final_challenge():
            print("is not final challenge")
            if self.prerequisite.has_enough_user_reviews(user):
                print("prerequisite has enough user reviews")
                return True
            else:
                print("prerequisite has not enough user reviews")
                return False

        # for the final challenge to be enabled
        # the prerequisite must have enough (3) user reviews
        # and the stack must have enough peer reviews
        else:
            print("is final challenge")
            if not self.prerequisite.has_enough_user_reviews(user):
                print("prerequisite has not enough user reviews")
                return False
            print("prerequisite has enough user reviews")
            if self.get_stack().has_enough_peer_reviews(user):
                print("has enough peer reviews")
                return True
            else:
                print("has not enough peer reviews")
                return False
        raise Exception("this case is not supposed to happen")

    def get_status(self, user):
        # there is no proper status for challenges that are not enabled
        if not self.is_enabled_for_user(user):
            return self.NOT_ENABLED

        elaboration = self.get_elaboration(user)

        # user did not start to write an elaboration
        if not elaboration:
            return self.NOT_STARTED

        # user started to write but did not yet submit an elaboration
        if not elaboration.is_submitted():
            return self.NOT_SUBMITTED

        # for normal peer review challenges
        if not self.is_final_challenge():
            # user received at least one bad review for his submission
            if not elaboration.is_passing_peer_review():
                return self.BLOCKED_BAD_REVIEW

            # user did not complete 3 user reviews for this challenge
            if not self.has_enough_user_reviews(user):
                return self.USER_REVIEW_MISSING

            # user is done but needs peer reviews for final challenge
            if not elaboration.is_reviewed_2times():
                return self.DONE_MISSING_PEER_REVIEW

            # user is done and passed at least 2 peer reviews
            else:
                return self.DONE_PEER_REVIEWED

        # for the final challenge
        else:
            # final challenge not evaluated yet
            if not elaboration.is_evaluated():
                return self.WAITING_FOR_EVALUATION
            # all done this stack is completed
            else:
                return self.EVALUATED
