from Course.models import Course, CourseUserRelation
from Review.models import ReviewEvaluation
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    help = 'Prints user result data for given course short title e.g.: python manage.py endterm_eval_users gsi'

    def handle(self, *args, **options):
        """
        user_MNr user_nickname user_vorname user_nachname user_studienkennzahl userLastActivity_date ReviewEvaluationsDone_percent user_statement TAGS_liste
            wobei TAGS_liste = tag1|tag2|tag3|tag4|tag5... (also tag1+’|’+tag2+’|’+usw)
        """
        try:
            course_short_title = args[0]
        except IndexError:
            print(self.help)
            exit(1)
        course = Course.get_or_raise_404(course_short_title)

        for relation in CourseUserRelation.objects.filter(user__is_staff=False, course=course):
            user = relation.user
            tags = []
            for tag in user.tags.all():
                tags.append(str(tag))


            tags_text = '|'.join(tags)
            if tags_text == '':
                tags_text = None
            s = "\t".join(["{}"] * 9).format(
                user.matriculation_number,
                user.nickname,
                user.first_name,
                user.last_name,
                user.study_code,
                str(user.last_activity),
                '{0:.2f}'.format(ReviewEvaluation.get_review_evaluation_percent(user, course)),
                user.statement,
                tags_text
            )

            print(s)
