from django.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import redirect
from Course.models import Course
from Stack.models import Stack


def home(request):
    if request.user.is_authenticated():
        data = {}
        gsi = Course.objects.get(short_title='gsi')
        course_stacks = Stack.objects.all().filter(course=gsi)
        data['course_stacks'] = []
        points_sum = 0
        for stack in course_stacks:
            data['course_stacks'].append({
                'stack': stack,
                'points': stack.get_points(request.user)
            })
            points_sum += stack.get_points(request.user)
        data['sum'] = points_sum
        return render_to_response('home.html', data, context_instance=RequestContext(request))
    else:
        return redirect('/login')
