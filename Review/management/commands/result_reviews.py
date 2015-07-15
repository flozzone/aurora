from django.core.management.base import NoArgsCommand
from AuroraProject.views import get_result_reviews

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        """
        ReviewID Task_ID AuthorOfReviewedElab_MNr ReviewedElab_ID ReviewAuthor_MNr ReviewPublicFields_∑chars ReviewLVAteamFields_∑chars ReviewEvaluation_value  FullText
            wobei FullText = ReviewFrage1_ID+':'+Answer1_Text+'¶'+ReviewFrage2_ID+':'+Answer2_Text+'¶'+usw.
            und alle CR in <br> und alle TAB in <tab>
        """

        result = get_result_reviews()

        print(result)
