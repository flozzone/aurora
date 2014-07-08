__author__ = 'queltos'

from django.core.management.base import NoArgsCommand
from Elaboration.models import Elaboration
from Challenge.models import Challenge
from Review.models import Review

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        """
        username (mnr) TAB elabID TAB challenge-title TAB challenge-ID TAB creation time TAB submission time TAB
        reviewID 1 TAB review-verdict 1 TAB review-creation-date 1 TAB review-submission-date 1 TAB reviewID 2 TAB
        review-verdict 2 TAB review-creation-date 2 TAB review-submission-date 2 TAB usw.
        """

        final_challenge_ids = Challenge.get_final_challenge_ids()
        elabs = Elaboration.objects.exclude(challenge__id__in=final_challenge_ids).prefetch_related()

        for elab in elabs:
            s = "\t".join(["{}"] * 15).format(
                elab.user.matriculation_number,
                elab.id,
                elab.challenge.title,
                elab.challenge.id,
                elab.creation_time,
                elab.submission_time
            )

            for review in Review.objects.filter(elaboration=elab):
                s += "\t" + review.id
                s += "\t" + review.appraisal
                s += "\t" + review.creation_time
                s += "\t" + review.submission_time

            print(s)
