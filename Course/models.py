from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
import Challenge.models


class Course(models.Model):
    title = models.CharField(max_length=100, unique=True)
    short_title = models.CharField(max_length=10, unique=True)
    description = models.TextField()
    course_number = models.CharField(max_length=100, unique=True)

    def __unicode__(self):
        return str(self.title)

    def __str__(self):
        return str(self.title)

    def get_course_challenges(self):
        challenges = Challenge.models.Challenge.objects.filter(course=self)
        return list(challenges)

    def user_is_enlisted(self, user):
        try:
            CourseUserRelation.objects.get(user=user, course=self)
            return True
        except CourseUserRelation.DoesNotExist:
            return False

    @staticmethod
    def get_or_raise_404(short_title):
        try:
            return Course.objects.get(short_title=short_title)
        except ObjectDoesNotExist:
            raise Http404


class CourseUserRelation(models.Model):
    user = models.ForeignKey('AuroraUser.AuroraUser')
    course = models.ForeignKey(Course)
