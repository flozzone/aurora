from AuroraUser.models import AuroraUser
from Course.models import CourseUserRelation, Course


def general_context_processor(request):
    context = {}
    user = AuroraUser.objects.filter(id=request.user.id)
    if user:
        user = user[0]
        context['user'] = user
        available_courses = []
        for course_user_relation in CourseUserRelation.objects.filter(user=user):
            available_courses.append(course_user_relation.course)
        if available_courses:
            context['available_courses'] = available_courses
    return context