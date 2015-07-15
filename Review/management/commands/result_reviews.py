from django.core.management.base import BaseCommand
from AuroraProject.views import get_result_reviews

class Command(BaseCommand):

    help = 'Prints review data for given course short title e.g.: python manage.py result_reviews gsi'

    def handle(self, *args, **options):
        """
        ReviewID Task_ID AuthorOfReviewedElab_MNr ReviewedElab_ID ReviewAuthor_MNr ReviewPublicFields_∑chars ReviewLVAteamFields_∑chars ReviewEvaluation_value  FullText
            wobei FullText = ReviewFrage1_ID+':'+Answer1_Text+'¶'+ReviewFrage2_ID+':'+Answer2_Text+'¶'+usw.
            und alle CR in <br> und alle TAB in <tab>
        """
        if len(args) is not 1:
            print(help)
            exit()
        result = get_result_reviews(args[0])

        print(result)