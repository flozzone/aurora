from datetime import datetime, timedelta
import os

from django.db import models
from django.contrib.contenttypes.fields import GenericRelation

from Comments.models import Comment
from Stack.models import StackChallengeRelation
from Review.models import Review
from Elaboration.models import Elaboration
from Course.models import Course


def challenge_image_path(instance, filename):
    name = 'challenge_%s' % instance.id
    fullname = os.path.join(instance.upload_path, name)
    if os.path.exists(fullname):
        os.remove(fullname)
    return fullname


class Challenge(models.Model):
    reviews_per_challenge = 3
    upload_path = 'challenge'
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=100)
    prerequisite = models.ForeignKey('self', null=True, blank=True)
    description = models.TextField()
    points = models.IntegerField(null=True)
    image = models.ImageField(upload_to=challenge_image_path, null=True, blank=True)
    # This is a comma separated list of mime types or file extensions. Eg.: image/*,application/pdf,.psd.
    accepted_files = models.CharField(max_length=100, default="image/*,application/pdf", blank=True)
    course = models.ForeignKey(Course)
    comments = GenericRelation(Comment)

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
        -1: "Can not be submitted yet.",
        0: "Not started (Click the green right-arrow-button).",
        1: "Not submitted.",
        2: "Waiting for you to write a review (click green pen)",
        3: "Bad review. We need to look at this. Please be patient.",
        4: "Done, waiting for reviews by others.",  # can proceed but will be a problem for final challenge
        5: "Done, peer reviewed.",
        6: "Waiting for evaluation.",
        7: "Evaluated."
    }

    next_dict = {
        -1: "Not enabled...",
        0: "Start a new task.",
        1: "Finish and submit your current task.",
        2: "Write a review.",
        3: "Blocked by negative review.",
        4: "Waiting for more reviews.",
        5: "All reviews are in, you can start the final task.",
        6: "Still waiting for evaluation of final task.",
        7: "Final task evaluated. Points received: "
    }

    def __str__(self):
        return u'%s' % self.title

    def get_course(self):
        return self.course

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

    def is_started(self, user):
        elaboration = self.get_elaboration(user)
        if elaboration is None:
            return False
        return elaboration.is_started()

    def get_stack(self):
        stack_challenge_relation = StackChallengeRelation.objects.filter(challenge=self)
        if stack_challenge_relation:
            return stack_challenge_relation[0].stack
        else:
            return None

    def is_first_challenge(self):
        return not self.prerequisite  # challenge without prerequisite is the first challenge

    @staticmethod
    def get_final_challenge_ids():
        peer_review_challenges = (
            Challenge.objects
            .filter(prerequisite__isnull=False).values_list('prerequisite', flat=True)
        )
        final_challenge_ids = (
            Challenge.objects
            .exclude(id__in=list(peer_review_challenges))
            .values_list('id', flat=True)
        )
        return final_challenge_ids

    @staticmethod
    def get_course_final_challenge_ids(course):
        peer_review_challenges = (
            Challenge.objects
            .filter(prerequisite__isnull=False).values_list('prerequisite', flat=True)
        )
        non_course_challenges = [challenge.id for challenge in Challenge.objects.exclude(course=course)]
        knockout_list = non_course_challenges + list(peer_review_challenges)
        final_challenge_ids = (
            Challenge.objects
            .exclude(id__in=knockout_list)
            .values_list('id', flat=True)
        )
        return final_challenge_ids

    def is_final_challenge(self):
        return False if self.get_next() else True

    def get_first_challenge(self):
        first_challenge = self
        while first_challenge.prerequisite is not None:
            first_challenge = first_challenge.prerequisite
        return first_challenge

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
        # all reviews for this elaboration written by this user
        reviews = Review.objects.filter(elaboration__challenge=self, reviewer=user)
        # exclude the reviews that are not submitted
        reviews = reviews.exclude(submission_time__isnull=True)
        return reviews

    def get_elaborations(self):
        submissions = Elaboration.objects.filter(challenge=self)
        return submissions

    def get_elab_count(self):
        return Elaboration.objects.filter(challenge=self).count()

    def get_sub_elab_count(self):
        return Elaboration.objects.filter(challenge=self, submission_time__isnull=False).count()

    def get_status_text(self, user):
        status = self.get_status(user)
        status_text = self.status_dict[status]
        next_text = self.next_dict[status]
        return {
            'status': status_text,
            'next': next_text
        }

    def is_enabled_for_user(self, user):
        # if user is not enlisted for the course the challenge is in,
        # the challenge can not be enabled for the user
        if not self.course.user_is_enlisted(user):
            return False

        # first challenge is always enabled
        if self.is_first_challenge():
            return True

        # if challenge is already submitted it is enabled by default
        elaboration = self.get_elaboration(user)
        if elaboration:
            if elaboration.is_submitted():
                return True

        # if not final challenge the prerequisite must have enough (3) user reviews
        if not self.is_final_challenge():
            if self.prerequisite.has_enough_user_reviews(user):
                return True
            else:
                return False

        # for the final challenge to be enabled
        # the prerequisite must have enough (3) user reviews,
        # the stack must not be blocked (by a bad review)
        # and the stack must have enough peer reviews
        else:
            if not self.prerequisite.has_enough_user_reviews(user):
                return False
            if self.get_stack().is_blocked(user):
                return False
            if self.get_stack().has_enough_peer_reviews(user):
                return True
            else:
                return False
        raise Exception("this case is not supposed to happen")

    def get_status(self, user):
        # there is no proper status for challenges that are not enabled
        if not self.is_enabled_for_user(user):
            return self.NOT_ENABLED

        elaboration = self.get_elaboration(user)

        # user did not start to write an elaboration
        if not elaboration or not elaboration.is_started():
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
            if not self.get_stack().has_enough_peer_reviews(user):
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

    @staticmethod
    def get_questions(course):
        result = Challenge.objects.filter(
            course=course,
            comments__seen=False
        ).distinct()

        return result

    def is_in_lock_period(self, user, course):
        PERIOD = 11
        START_YEAR = 2015
        START_MONTH = 3
        START_DAY = 1

        final_challenge_ids = Challenge.get_course_final_challenge_ids(course)
        elaborations = (
            Elaboration.objects
            .filter(challenge__id__in=final_challenge_ids, user=user, submission_time__gt=datetime(START_YEAR, START_MONTH, START_DAY))
        )
        if elaborations:
            last_submit = elaborations.latest('submission_time')
            if last_submit.submission_time < (datetime.now() - timedelta(days=PERIOD)):
                return False
            else:
                return (last_submit.submission_time + timedelta(days=PERIOD))
        return False
