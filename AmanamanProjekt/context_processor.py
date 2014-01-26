from PortfolioUser.models import PortfolioUser
from Course.models import CourseUserRelation, Course


def general_context_processor(request):
    context = {}
    user = PortfolioUser.objects.filter(id=request.user.id)
    if user:
        user = user[0]
        context['user'] = user
        available_courses = []
        for course_user_relation in CourseUserRelation.objects.filter(user=user):
            available_courses.append(course_user_relation.course)
        if available_courses:
            context['available_courses'] = available_courses
        last_selected_course = user.last_selected_course
        if not last_selected_course:
            last_selected_course = available_courses[0]
            user.last_selected_course = last_selected_course
            user.save()
        context['last_selected_course'] = last_selected_course
    return context