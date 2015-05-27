from django.db import models


class Stack(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    course = models.ForeignKey('Course.Course')

    def get_first_challenge(self):
        for relation in StackChallengeRelation.objects.filter(stack=self):
            return relation.challenge.get_first_challenge()
        return None

    def get_final_challenge(self):
        for relation in StackChallengeRelation.objects.filter(stack=self):
            return relation.challenge.get_final_challenge()
        return None

    def get_challenges(self):
        challenges = []
        for relation in StackChallengeRelation.objects.filter(stack=self):
            challenges.append(relation.challenge)
        return challenges

    def get_challenge_image_urls(self):
        challenge_image_urls = []
        for challenge in self.get_challenges():
            challenge_image_urls.append(challenge.image.url)
        return challenge_image_urls

    def is_started(self, user):
        return self.get_first_challenge().is_started(user)

    def is_evaluated(self, user):
        elaboration = self.get_final_challenge().get_elaboration(user)
        if elaboration is None:
            return False
        return elaboration.is_evaluated()

    def get_points_earned(self, user):
        final_challenge = self.get_final_challenge()
        elaboration = final_challenge.get_elaboration(user)
        if not elaboration:
            return 0
        evaluation = elaboration.get_evaluation()
        if not evaluation:
            return 0
        return evaluation.evaluation_points

    def get_points_available(self):
        points = 0
        for challenge in self.get_challenges():
            points += challenge.points
        return points

    def get_last_available_challenge(self, user):
        available_challenge = None
        for challenge in self.get_challenges():
            if challenge.is_enabled_for_user(user):
                available_challenge = challenge
        return available_challenge

    def get_status_text(self, user):
        last_available_challenge = self.get_last_available_challenge(user)
        return last_available_challenge.get_status_text(user)

    def is_blocked(self, user):
        for challenge in self.get_challenges():
            if not challenge.is_final_challenge():
                elaboration = challenge.get_elaboration(user)
                if elaboration:
                    if not elaboration.is_passing_peer_review():
                        return True
        return False

    def has_enough_peer_reviews(self, user):
        for challenge in self.get_challenges():
            if not challenge.is_final_challenge():
                elaboration = challenge.get_elaboration(user)
                if not elaboration:
                    # this should never happen
                    return False
                if not elaboration.is_reviewed_2times():
                    return False
        return True

    def __str__(self):
        return u'%s' % self.title

class StackChallengeRelation(models.Model):
    stack = models.ForeignKey('Stack.Stack')
    challenge = models.ForeignKey('Challenge.Challenge')