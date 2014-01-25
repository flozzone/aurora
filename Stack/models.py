from django.db import models
from Evaluation.models import Evaluation
from Elaboration.models import Elaboration


class Stack(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    course = models.ForeignKey('Course.Course')

    def get_root_challenge(self):
        for relation in StackChallengeRelation.objects.filter(stack=self):
            if relation.challenge.prerequisite:
                return relation.challenge

    def get_challenges(self):
        challenges = []
        for relation in StackChallengeRelation.objects.filter(stack=self):
            challenges.append(relation.challenge)
        return challenges

    def get_challenge_image_urls(self):
        challenge_image_urls = []
        for challenge in self.get_challenges():
            challenge_image_urls.append(challenge.image_url)
        return challenge_image_urls

    def get_points(self, user):
        for challenge in self.get_challenges():
            if challenge.is_final_challenge():
                elaboration = None
                evaluation = None
                elaboration = Elaboration.objects.filter(challenge=challenge, user=user)
                if elaboration:
                    evaluation = Evaluation.objects.filter(submission=elaboration[0])
                if evaluation:
                    return evaluation[0].evaluation_points
        return 0

    def get_last_available_challenge(self, user):
        available_challenge = None
        for challenge in self.get_challenges():
            if challenge.is_enabled_for_user(user):
                available_challenge = challenge
        return available_challenge

    def get_status_text(self, user):
        last_available_challenge = self.get_last_available_challenge(user)
        print(last_available_challenge.title)
        return last_available_challenge.get_status_text(user)

class StackChallengeRelation(models.Model):
    stack = models.ForeignKey('Stack.Stack')
    challenge = models.ForeignKey('Challenge.Challenge')