from django.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import redirect
from Stack.models import Stack


def home(request):
    if request.user.is_authenticated():
        data = {}
        user = RequestContext(request)['user']
        course = RequestContext(request)['last_selected_course']
        course_stacks = Stack.objects.all().filter(course=course)
        data['course_stacks'] = []
        points_sum = 0
        for stack in course_stacks:
            data['course_stacks'].append({
                'stack': stack,
                'points': stack.get_points(user)
            })
            points_sum += stack.get_points(user)
        data['sum'] = points_sum
        return render_to_response('home.html', data, context_instance=RequestContext(request))
    else:
        return redirect('/login')
