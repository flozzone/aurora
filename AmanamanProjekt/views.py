from django.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import redirect

from Comments.models import CommentReferenceObject
from Stack.models import Stack
from Course.models import Course, CourseUserRelation


def home(request):
    if request.user.is_authenticated():
        data = {}
        user = RequestContext(request)['user']

        course_ids = CourseUserRelation.objects.filter(user=user).values_list('course', flat=True)
        courses = Course.objects.filter(id__in=course_ids)
        data['courses'] = courses
        data['stacks'] = []
        for course in courses:
            stack_data = {}
            course_stacks = Stack.objects.all().filter(course=course)
            stack_data['course_title'] = course.title
            stack_data['course_stacks'] = []
            points_sum = 0
            for stack in course_stacks:
                stack_data['course_stacks'].append({
                    'stack': stack,
                    'points': stack.get_points(user)
                })
                points_sum += stack.get_points(user)
            stack_data['sum'] = points_sum
            data['stacks'].append(stack_data)

        try:
            o = CommentReferenceObject.objects.get(name='newsfeed')
        except CommentReferenceObject.DoesNotExist:
            o = CommentReferenceObject(name='newsfeed')
            o.save()

        context = RequestContext(request, {'newsfeed': o})

        return render_to_response('home.html', data, context)
    elif 'sKey' in request.GET:
        from PortfolioUser.views import sso_auth_callback

        return sso_auth_callback(request)

        # from django.http import QueryDict

        # q = QueryDict('', mutable=True)
        # for key in request.GET.keys():
        #     q[key] = request.GET[key]
        # print(q)
        # url = '/sso_auth_callback?' + q.urlencode()
        # print(url)
        # return redirect(url)
    else:
        return redirect('/login')
