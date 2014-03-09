from django.db import models


class Course(models.Model):
    title = models.CharField(max_length=100)
    short_title = models.CharField(max_length=10)
    description = models.TextField()
    course_number = models.CharField(max_length=100)

    def __unicode__(self):
        return str(self.title)

    def get_course_challenges(self):
        challenges = []
        ccrs = CourseChallengeRelation.objects.filter(course=self)
        for ccr in ccrs:
            challenges.append(ccr.challenge)
        return challenges

    def user_is_enlisted(self, user):
        try:
            CourseUserRelation.objects.get(user=user, course=self)
            return True
        except CourseUserRelation.DoesNotExist:
            return False


class CourseUserRelation(models.Model):
    user = models.ForeignKey('PortfolioUser.PortfolioUser')
    course = models.ForeignKey(Course)


class CourseChallengeRelation(models.Model):
    challenge = models.ForeignKey('Challenge.Challenge')
    course = models.ForeignKey(Course)