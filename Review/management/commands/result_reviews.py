__author__ = 'dan'

from Review.models import Review
from ReviewAnswer.models import ReviewAnswer
from django.core.management.base import NoArgsCommand
from datetime import datetime

from AmanamanProjekt.views import get_result_reviews

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

        result = get_result_reviews()

        print(result)
