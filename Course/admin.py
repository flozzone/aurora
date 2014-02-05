from django.contrib import admin
from Course.models import Course
from Course.models import CourseUserRelation
from Course.models import CourseChallengeRelation

admin.site.register(Course)
admin.site.register(CourseUserRelation)
admin.site.register(CourseChallengeRelation)
