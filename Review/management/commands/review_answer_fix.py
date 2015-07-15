from Review.models import Review
from ReviewQuestion.models import ReviewQuestion
from ReviewAnswer.models import ReviewAnswer
from django.core.management.base import NoArgsCommand


class Command(NoArgsCommand):
    def handle_noargs(self, **options):

        reviews = Review.objects.filter(submission_time__isnull=False)

        problems = []
        for review in reviews:
            for review_question in ReviewQuestion.objects.filter(challenge=review.elaboration.challenge):
                answers = ReviewAnswer.objects.filter(review=review, review_question=review_question)
                if len(answers) is 0:
                    problems.append(review)


        script_review_text = "[diese review-antwort ging leider verloren, und wurde von einem script durch diesen text ersetzt]"

        count = 0
        for review in problems:
            for review_question in ReviewQuestion.objects.filter(challenge=review.elaboration.challenge):
                answers = ReviewAnswer.objects.filter(review=review, review_question=review_question)
                if len(answers) is 0:
                    ReviewAnswer(review=review, review_question=review_question, text= script_review_text).save()
                    count += 1

        print(count)
        print('All done :D')