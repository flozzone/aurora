__author__ = 'dan'

from Review.models import Review
from ReviewAnswer.models import ReviewAnswer
from django.core.management.base import NoArgsCommand
from datetime import datetime

def time_to_unix_string(time):
    if time is None:
        return str(None)

    delta = time - datetime(1970, 1, 1)
    hours = delta.days * 24
    seconds = hours * 3600
    seconds += delta.seconds
    return str(seconds)

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        """
        review-autor (MNr) TAB
        reviewed-elab-autor (MNr) TAB
        reviewed-elab-challenge-ID TAB
        review-creation-date TAB
        review-submission-date TAB
        länge des reviews (number of chars of all fields summiert)
        """
        reviews = Review.objects.all().prefetch_related()
        result = ""
        for review in reviews:
            answers = ReviewAnswer.objects.filter(review=review.id)
            answer_string = ""
            for answer in answers:
                answer_string += answer.text
            length = len(answer_string)

            result = "\t".join(["{}"] * 6).format(
                review.reviewer.matriculation_number,
                review.elaboration.user.matriculation_number,
                review.elaboration.challenge_id,
                time_to_unix_string(review.creation_time),
                time_to_unix_string(review.submission_time),
                str(length)
            )

            print(result)
