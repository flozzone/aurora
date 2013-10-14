from django.db import models


class Course(models.Model):
    title = models.CharField(max_length=100)
    short_title = models.CharField(max_length=10)
    description = models.TextField()
    course_number = models.CharField(max_length=100)


class CourseUserRelation(models.Model):
    user = models.ForeignKey('PortfolioUser.PortfolioUser')
    course = models.ForeignKey(Course)


"""
class CourseChallengeRelation(models.Model):
    course = models.ForeignKey(Course)
    main_challenge = models.ForeignKey('challenge.MainChallenge')

    def __unicode__(self):
        return str(self.id)


class GradeInfo(models.Model):
    grade = models.IntegerField()
    min = models.IntegerField()

    def __unicode__(self):
        return str(self.id)


class CourseGradeRelation(models.Model):
    course = models.ForeignKey(Course)
    grade_info = models.ForeignKey(GradeInfo)

    def __unicode__(self):
        return str(self.id)
"""