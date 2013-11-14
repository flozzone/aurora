from django.db import models
from Challenge.models import Challenge


class Course(models.Model):
    title = models.CharField(max_length=100)
    short_title = models.CharField(max_length=10)
    description = models.TextField()
    course_number = models.CharField(max_length=100)

    def get_course_challenges(course_short_title):
        challenges = []
        ccrs = CourseChallengeRelation.objects.filter(course__short_title=course_short_title)
        for ccr in ccrs:
            challenges.append(ccr.challenge)
        return challenges

class CourseUserRelation(models.Model):
    user = models.ForeignKey('PortfolioUser.PortfolioUser')
    course = models.ForeignKey(Course)

class CourseChallengeRelation(models.Model):
    challenge = models.ForeignKey('Challenge.Challenge')
    course = models.ForeignKey(Course)