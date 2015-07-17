from Course.models import Course
from Evaluation.models import Evaluation
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    help = 'Prints final task elaboration data for given course short title e.g.: python manage.py endterm_eval_elabs_final gsi'

    def handle(self, *args, **options):
        """
        Author_MNr Elab_ID Challenge_ID creation_time submission_time Evaluation_ID EvalTutor_ID EvalCreation_date EvalSubmission_date Eval_points ElabComments_count
        """
        try:
            course_short_title = args[0]
        except IndexError:
            print(self.help)
            exit(1)

        course = Course.get_or_raise_404(course_short_title)

        evals = Evaluation.objects.filter(submission__challenge__course=course).prefetch_related()
        for eval in evals:
            elab = eval.submission
            s = "\t".join(["{}"] * 11).format(
                elab.user.matriculation_number,
                elab.id,
                elab.challenge.id,
                elab.creation_time,
                elab.submission_time,
                eval.id,
                eval.tutor.id,
                eval.creation_date,
                eval.submission_time,
                eval.evaluation_points,
                eval.submission.get_visible_comments_count()
            )

            print(s)
