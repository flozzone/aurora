from django.contrib import admin
from Course.models import Course
from Course.models import CourseUserRelation
from Course.models import CourseChallengeRelation

class CourseAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None, {
                'fields': [
                    'title',
                    'short_title',
                    'description',
                    'course_number',
                ]
            }
        ),
    ]
    list_display = ('id', 'title', 'short_title', 'description', 'course_number', )

admin.site.register(Course, CourseAdmin)


class CourseUserRelationAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None, {
                'fields': [
                    'user',
                    'course',
                ]
            }
        ),
    ]
    list_display = ('id', 'user', 'course', )

admin.site.register(CourseUserRelation, CourseUserRelationAdmin)


class CourseChallengeRelationAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None, {
                'fields': [
                    'challenge',
                    'course',
                ]
            }
        ),
    ]
    list_display = ('id', 'challenge', 'course', )

admin.site.register(CourseChallengeRelation, CourseChallengeRelationAdmin)