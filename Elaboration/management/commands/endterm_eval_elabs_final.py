__author__ = 'queltos'

from django.core.management.base import NoArgsCommand
from Evaluation.models import Evaluation

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        """
        username(mnr) TAB elabID TAB challenge-title TAB challenge-ID TAB creation time TAB submission time TAB
        evaluationID TAB tutor TAB evaluation-creationdate TAB evaluation-submissiontime TAB evaluation-points
        """

        evals = Evaluation.objects.all().prefetch_related()

        for eval in evals:
            elab = eval.submission
            s = "\t".join(["{}"] * 11).format(
                elab.user.username + " (" + str(elab.user.matriculation_number) + ")",
                str(elab.id),
                elab.challenge.title,
                str(elab.challenge.id),
                str(elab.creation_time),
                str(elab.submission_time),
                eval.id,
                eval.tutor.display_name,
                str(eval.creation_date),
                str(eval.submission_time),
                str(eval.evaluation_points)
            )

            print(s)
