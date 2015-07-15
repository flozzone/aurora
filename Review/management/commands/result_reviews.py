__author__ = 'dan'

from Review.models import Review
from ReviewAnswer.models import ReviewAnswer
from django.core.management.base import NoArgsCommand
from datetime import datetime

from AuroraProject.views import get_result_reviews

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
        ReviewID Task_ID AuthorOfReviewedElab_MNr ReviewedElab_ID ReviewAuthor_MNr ReviewPublicFields_∑chars ReviewLVAteamFields_∑chars ReviewEvaluation_value  FullText
            wobei FullText = ReviewFrage1_ID+':'+Answer1_Text+'¶'+ReviewFrage2_ID+':'+Answer2_Text+'¶'+usw.
            und alle CR in <br> und alle TAB in <tab>
        """

        result = get_result_reviews()

        print(result)
