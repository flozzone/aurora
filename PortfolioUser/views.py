from django.views.decorators.http import require_GET
import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth import authenticate, login as django_login, logout
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from PortfolioUser.models import PortfolioUser
from datetime import datetime

from Course.models import Course

import hashlib
import hmac
from local_settings import SSO_SHARED_SECRET, SSO_URI


@csrf_exempt
def signin(request):
    if request.method == 'POST':
        if 'username' in request.POST and 'password' in request.POST and 'remember' in request.POST:
            if request.POST['remember'] == 'false':
                request.session.set_expiry(0)
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)

            if user is not None:
                if user.is_active:
                    django_login(request, user)
                    response_data = {'success': True}
                    # fetch gravatar img on first login
                    if not PortfolioUser.objects.all().get(id=user.id).avatar:
                        PortfolioUser.objects.all().get(id=user.id).get_gravatar()
                    return HttpResponse(json.dumps(response_data), content_type="application/json")
                else:
                    response_data = {'success': False, 'message': 'Your account has been disabled!'}
                    return HttpResponse(json.dumps(response_data), content_type="application/json")
            else:
                response_data = {'success': False, 'message': 'Your username and password were incorrect.'}
                return HttpResponse(json.dumps(response_data), content_type="application/json")
    else:
        response_data = {'success': False, 'message': 'only POST allowed for this url'}
        return HttpResponse(json.dumps(response_data), content_type="application/json")


def signout(request):
    logout(request)
    response_data = {'success': True}
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def login(request):
    if 'next' in request.GET:
        return render_to_response('login.html', {'next': request.GET['next']}, context_instance=RequestContext(request))
    else:
        return render_to_response('login.html', {'next': '/'}, context_instance=RequestContext(request))


def sso_auth_redirect():
    return redirect(SSO_URI)


@require_GET
def sso_auth_callback(request):
    values = request.GET
    if sso_authenticate(values):
        # TODO set up session here
        pass


def sso_authenticate(params):
    if 'sKey' in params.keys():
        hmac_received = params['sKey']
    elif 'logout' in params.keys():
        hmac_received = params['logout']

    values = ''
    for key in ['oid', 'mn', 'firstName', 'lastName', 'mail']:
        values += params[key]

    shared_secret = SSO_SHARED_SECRET.encode(encoding='latin1')
    now = datetime.utcnow() - datetime.datetime(1970, 1, 1).total_seconds()
    for offset in [0, -1, 1, -2, 2]:
        values_string = values + str(now + offset)
        values_string = values_string.encode(encoding='latin1')
        hmac_calced = hmac.new(shared_secret, values_string, hashlib.sha1).hexdigest()

        if hmac_calced == hmac_received:
            return True

    return False


@login_required
@ensure_csrf_cookie
def profile(request):
    user = RequestContext(request)['user']
    return render_to_response('profile.html', {'user': user}, context_instance=RequestContext(request))

@login_required()
def profile_save(request):
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

    users_with_same_nickname = PortfolioUser.objects.filter(nickname=request.POST['nickname'])
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
        course = Course.objects.filter(short_title=request.POST['short_title'])
        if course:
            course = course[0]
            user.last_selected_course = course
            user.save()
        response_data['success'] = True
    return HttpResponse(json.dumps(response_data), content_type="application/json")