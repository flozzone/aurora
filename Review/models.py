from django.db import models

class Review(models.Model):
    elaboration = models.ForeignKey('Elaboration.Elaboration')
    creation_time = models.DateTimeField(auto_now_add=True)
    submission_time = models.DateTimeField(null=True)
    reviewer = models.ForeignKey('PortfolioUser.PortfolioUser')
    NOTHING = 'N'
    FAIL = 'F'
    SUCCESS = 'S'
    APPRAISAL_CHOICES = (
        (NOTHING, 'Not even trying'),
        (FAIL, 'Fail'),
        (SUCCESS, 'Success'),
    )
    appraisal = models.CharField(max_length=1,
                                 choices=APPRAISAL_CHOICES,
                                 default=NOTHING)
    awesome = models.BooleanField(default=False)

    def getElaborationAuthor(self):
        return self.elaboration.user

    @staticmethod
    def getOpenReview(challenge, user):
        open_reviews = Review.objects.filter(elaboration__challenge=challenge, submission_time__isnull=True)
        print(open_reviews)
        open_reviews = open_reviews.exclude(elaboration__user=user)
        print(open_reviews)
        if (open_reviews):
            return open_reviews[0]
        else:
            return None

    @staticmethod
    def getReviewAmount(elaboration):
        return len(Review.objects.filter(elaboration=elaboration).exclude(submission_time__isnull=True))

