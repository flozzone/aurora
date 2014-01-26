from django.db import models


class Notification(models.Model):
    user = models.ForeignKey('PortfolioUser.PortfolioUser')
    course = models.ForeignKey('Course.Course')
    text = models.CharField(max_length=100)
    image_url = models.CharField(max_length=100, default="/static/img/info.jpg")
    link = models.CharField(max_length=100, default="")
    creation_time = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    BAD_REVIEW = "Unfortunately you received a bad review for challenge: "
    ENOUGH_PEER_REVIEWS = "You have received enough positive reviews to submit your final challenge: "
    SUBMISSION_EVALUATED = "Your submission was evaluated: "
    NEW_MESSAGE = "New message for your submission: "