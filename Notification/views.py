from django.core import urlresolvers
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from Notification.models import Notification
from AuroraUser.models import AuroraUser
from Course.models import Course, CourseUserRelation


@login_required()
def notifications(request, course_short_title=None):
    data = {}
    user = RequestContext(request)['user']
    course = Course.get_or_raise_404(course_short_title)

    if 'id' in request.GET:
        try:
            notification = Notification.objects.get(pk=request.GET['id'])
            if not notification.user == user:
                raise Http404
        except:
            raise Http404

        notification.read = True
        notification.save()

        if 'link' in request.GET:
            return redirect(request.GET['link'])

        return redirect('Notification:list', course_short_title=course_short_title)
    notifications = Notification.objects.filter(user=user, course=course).order_by('-creation_time')
    data['notifications'] = notifications
    data['course'] = course
    return render_to_response('notifications.html', data, context_instance=RequestContext(request))


@login_required()
@staff_member_required
def write_notification(request, course_short_title=None):
    if not 'user' in request.GET:
        raise Http404
    data = {
        'user_id': request.GET['user'],
    }
    return render_to_response('send_notification.html', data, context_instance=RequestContext(request))


@login_required()
@staff_member_required
def send_notification(request, course_short_title=None):
    if not 'user_id' in request.POST:
        raise Http404
    if not 'message' in request.POST:
        raise Http404
    user = AuroraUser.objects.get(pk=request.POST['user_id'])
    text = request.POST['message']
    course_ids = CourseUserRelation.objects.filter(user=user).values_list('course', flat=True)
    courses = Course.objects.filter(id__in=course_ids)
    for course in courses:
        obj, created = Notification.objects.get_or_create(
            user=user,
            course=course,
            text=text,
            link=""
        )
    return HttpResponse("Notification sent to user with id: %s" % user.nickname)


@login_required()
def read(request, course_short_title=None):
    user = RequestContext(request)['user']
    course = Course.get_or_raise_404(course_short_title)
    notifications = Notification.objects.filter(user=user, course=course)
    for notification in notifications:
        if not notification.user == user:
            raise Http404
        notification.read = True
        notification.save()
    return HttpResponse()


@login_required()
def refresh(request, course_short_title=None):
    user = RequestContext(request)['user']
    course = Course.get_or_raise_404(course_short_title)
    notifications = Notification.objects.filter(user=user, course=course, read=False)
    return HttpResponse(len(notifications))


