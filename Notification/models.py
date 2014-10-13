import os

from django.db import models

from AuroraProject.settings import STATIC_URL


class Notification(models.Model):
    user = models.ForeignKey('AuroraUser.AuroraUser')
    course = models.ForeignKey('Course.Course')
    text = models.CharField(max_length=100)
    image_url = models.CharField(max_length=100, default=os.path.join(STATIC_URL, 'img', 'info.jpg'))
    link = models.CharField(max_length=100, default="")
    creation_time = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    BAD_REVIEW = "Unfortunately you received a bad review for challenge: "
    ENOUGH_PEER_REVIEWS = "You have received enough positive reviews to submit your final challenge: "
    SUBMISSION_EVALUATED = "Your submission was evaluated: "
    NEW_MESSAGE = "New message for your submission: "

    @staticmethod
    def bad_review(review):
        text = Notification.truncate_text(Notification.BAD_REVIEW + review.elaboration.challenge.title)
        Notification(
            user=review.elaboration.user,
            course=review.elaboration.challenge.get_course(),
            text=text,
            image_url=review.elaboration.challenge.image.url,
            link="/challenges/challenge?id=" + str(review.elaboration.challenge.id)
        ).save()

    @staticmethod
    def enough_peer_reviews(review):
        final_challenge = review.elaboration.challenge.get_final_challenge()
        if final_challenge.is_enabled_for_user(review.elaboration.user) and not final_challenge.get_elaboration(review.elaboration.user):
            text = Notification.truncate_text(Notification.ENOUGH_PEER_REVIEWS + final_challenge.title)
            obj, created = Notification.objects.get_or_create(
                user=review.elaboration.user,
                course=review.elaboration.challenge.get_course(),
                text=text,
                image_url=final_challenge.image.url,
                link="/challenges/stack?id=" + str(review.elaboration.challenge.get_stack().id)
            )

    @staticmethod
    def truncate_text(text):
        if len(text) >= 100:
            text = text[0:96]
            text += "..."
        return text