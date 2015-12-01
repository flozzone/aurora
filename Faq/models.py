from django.db import models

from Course.models import Course


class Faq(models.Model):

    course = models.ManyToManyField(Course)
    question = models.TextField(null=False)
    answer = models.TextField(null=False)
    order = models.PositiveIntegerField()

    @staticmethod
    def get_faqs(course_short_title):
        return Faq.objects.filter(course__short_title=course_short_title)