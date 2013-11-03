from django.db import models


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


class StackChallengeRelation(models.Model):
    stack = models.ForeignKey('Stack.Stack')
    challenge = models.ForeignKey('Challenge.Challenge')