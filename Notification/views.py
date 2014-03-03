from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from Notification.models import Notification



@login_required()
def notifications(request):
    data = {}
    user = RequestContext(request)['user']
    course = RequestContext(request)['last_selected_course']

    if 'id' in request.GET:
        notification = Notification.objects.get(pk=request.GET['id'])
        notification.read = True
        notification.save()

        if 'link' in request.GET:
            redirect(request.GET['link'])
        return redirect('/notifications')
    notifications = Notification.objects.filter(user=user, course=course).order_by('-creation_time')
    data['notifications'] = notifications
    return render_to_response('notifications.html', data, context_instance=RequestContext(request))


@login_required()
def read(request):
    user = RequestContext(request)['user']
    course = RequestContext(request)['last_selected_course']
    notifications = Notification.objects.filter(user=user, course=course)
    for notification in notifications:
        notification.read = True
        notification.save()
    return HttpResponse()


@login_required()
def refresh(request):
    user = RequestContext(request)['user']
    course = RequestContext(request)['last_selected_course']
    notifications = Notification.objects.filter(user=user, course=course, read=False)
    return HttpResponse(len(notifications))


