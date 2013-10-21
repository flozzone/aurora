from django.db import models


class Course(models.Model):
    title = models.CharField(max_length=100)
    short_title = models.CharField(max_length=10)
    description = models.TextField()
    course_number = models.CharField(max_length=100)

class CourseUserRelation(models.Model):
    user = models.ForeignKey('PortfolioUser.PortfolioUser')
    course = models.ForeignKey(Course)

class CourseChallengeRelation(models.Model):
    challenge = models.ForeignKey('Challenge.Challenge')
    course = models.ForeignKey(Course)