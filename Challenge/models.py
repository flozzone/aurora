from django.db import models
from Stack.models import StackChallengeRelation
from ReviewQuestion.models import ReviewQuestion

class Challenge(models.Model):
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=100)
    prerequisite = models.ForeignKey('self', null=True)
    description = models.TextField()
    image_url = models.CharField(max_length=100)

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
            return stack_challenge_relation.stack
        else:
            return None

    def is_final_challenge(self):
        return False if self.get_next() else True

    def is_available_for_user(self, user):
        if self.prerequisite:
            return False
        else:
            return True

    def get_peer_review_questions(self):
        peer_review_questions = []
        for peer_review_question in ReviewQuestion.objects.filter(challenge=self).order_by('order'):
            peer_review_questions.append(peer_review_question)
        return peer_review_questions