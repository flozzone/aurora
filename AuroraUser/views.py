from django.views.decorators.http import require_GET, require_POST
import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth import authenticate, login as django_login, logout
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from AuroraUser.models import AuroraUser
from datetime import datetime
from django.core.urlresolvers import reverse

from Course.models import Course

from hashlib import sha1
from hmac import new as hmac_new
from django.conf import settings
from django.http import Http404


@require_POST
def signin(request, course_short_title=None):
    if 'username' not in request.POST or 'password' not in request.POST or 'remember' not in request.POST:
        response_data = {'success': False, 'message': 'Something went wrong. Please contact the LVA team'}
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    if request.POST['remember'] == 'false':
        request.session.set_expiry(0)

    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)

    if user is None:
        response_data = {'success': False, 'message': 'Your username or password was incorrect.'}
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    if not user.is_active:
        response_data = {'success': False, 'message': 'Your account has been disabled!'}
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    django_login(request, user)

    # fetch gravatar img on first login
    if not AuroraUser.objects.all().get(id=user.id).avatar:
        AuroraUser.objects.all().get(id=user.id).get_gravatar()

    response_data = {'success': True}
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def signout(request, course_short_title=None):
    logout(request)
    return redirect(reverse('home', args=(course_short_title,)))


@ensure_csrf_cookie
def login(request, course_short_title=None):
    next_url = ""
    if 'next_url' in request.session and request.session['next_url'] is not None:
        next_url = request.session['next_url']
    else:
        next_url = reverse('home', args=(course_short_title, ))

    sso_uri = settings.SSO_URI.replace("%%NEXT_URL%%", next_url)

    data = {
        'course': Course.get_or_raise_404(course_short_title),
        'signin_url': reverse('User:signin', args=(course_short_title, )),
        'next': next_url,
        'sso_uri': sso_uri
    }

    if 'error_message' in request.GET:
        data.update({'error_message': request.GET['error_message']})
        return render_to_response('login.html', data, context_instance=RequestContext(request))
    else:
        return render_to_response('login.html', data, context_instance=RequestContext(request))


@DeprecationWarning
def sso_auth_redirect():
    return redirect(settings.SSO_URI)


@require_GET
def sso_auth_callback(request):
    values = request.GET

    user = authenticate(params=values)

    if user is None:
        return redirect(reverse('course_selection'))
        # return render_to_response('login.html', {'error_message': 'Your user is not enrolled with this system'}, context_instance=RequestContext(request))

    if not user.is_active:
        return redirect(reverse('course_selection'))
        # return render_to_response('login.html', {'error_message': 'Your user has been deactivated'}, context_instance=RequestContext(request))

    django_login(request, user)

    if not user.avatar:
        user.get_gravatar()

    return redirect(reverse('course_selection'))


class ZidSSOBackend():
    def authenticate(self, params):
        param_keys = params.keys()

        if 'sKey' in param_keys:
            hmac_received = params['sKey']
        elif 'logout' in param_keys:
            hmac_received = params['logout']
        else:
            return None

        # make sure order is correct by creating a new list and putting in the available keys one by one
        values = ''
        for key in ['oid', 'mn', 'firstName', 'lastName', 'mail']:
            if key in param_keys:
                values += params[key]

        shared_secret = settings.SSO_SHARED_SECRET.encode(encoding='latin1')
        utc_now = (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds()
        now = int(utc_now / 10)
        user = None
        for offset in [0, -1, 1, -2, 2]:
            values_string = values + str(now + offset)
            values_string = values_string.encode(encoding='latin1')
            hmac_calced = hmac_new(shared_secret, values_string, sha1).hexdigest()

            if hmac_calced == hmac_received:
                try:
                    user = AuroraUser.objects.get(matriculation_number=params['mn'])
                except AuroraUser.DoesNotExist:
                    try:
                        user = AuroraUser.objects.get(oid=params['oid'])
                    except AuroraUser.DoesNotExist:
                        user = None

        return user

    def get_user(self, user_id):
        try:
            user = AuroraUser.objects.get(pk=user_id)
        except AuroraUser.DoesNotExist:
            user = None

        return user

    def __str__(self):
        return('ZidSSOBackend')

    def __unicode__(self):
        return('ZidSSOBackend')


@login_required
@ensure_csrf_cookie
def profile(request, course_short_title):
    user = RequestContext(request)['user']
    selected_course = Course.get_or_raise_404(course_short_title)
    return render_to_response('profile.html', {'user': user, 'course': selected_course}, context_instance=RequestContext(request))

@login_required()
def profile_save(request, course_short_title):
    data = {}
    user = RequestContext(request)['user']
    text_limit = 100
    valid_nickname = True
    if 'nickname' in request.POST and request.POST['nickname'] == "":
        data['error'] = "empty nickname not allowed"
        valid_nickname = False
    nickname_limit = 30
    if len(request.POST['nickname']) > nickname_limit:
        data['error'] = "nickname too long (%s character limit)" % nickname_limit
        valid_nickname = False

    users_with_same_nickname = AuroraUser.objects.filter(nickname=request.POST['nickname'])
    for user_with_same_nickname in users_with_same_nickname:
        if user.id is not user_with_same_nickname.id:
            data['error'] = "nickname already taken"
            valid_nickname = False

    if valid_nickname:
        user.nickname = request.POST['nickname']

    if is_valid_email(request.POST['email'], text_limit):
        user.email = request.POST['email']
    else:
        data['error'] = "not a valid email address"

    if 'file' in request.FILES:
        user.avatar = request.FILES['file']
    if len(request.POST['study_code']) < text_limit:
        user.study_code = request.POST['study_code']
    else:
        data['error'] = "not a valid study code"
    if len(request.POST['statement']) < text_limit:
        user.statement = request.POST['statement']
    else:
        data['error'] = "statement too long (%s character limit)" % text_limit
    user.save()
    data['nickname'] = user.nickname
    data['email'] = user.email
    data['study_code'] = user.study_code
    data['statement'] = user.statement
    return HttpResponse(json.dumps(data))

def is_valid_email(email, text_limit):
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError
    if len(email) > text_limit:
        return False
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


@login_required()
def course(request):
    user = RequestContext(request)['user']
    response_data = {}
    if request.method == 'POST':
        try:
            course = Course.objects.get(short_title=request.POST['short_title'])
            if not course.user_is_enlisted(user):
                raise Http404
        except:
            raise Http404
        if course:
            user.last_selected_course = course
            user.save()
        response_data['success'] = True
    return HttpResponse(json.dumps(response_data), content_type="application/json")