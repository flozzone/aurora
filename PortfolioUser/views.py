import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth import authenticate, login as django_login, logout
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from PortfolioUser.models import PortfolioUser
from Course.models import Course


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


@login_required()
def profile(request):
    user = RequestContext(request)['user']
    return render_to_response('profile.html', {'user': user}, context_instance=RequestContext(request))


@login_required()
def profile_save(request):
    data = {}
    user = RequestContext(request)['user']
    valid_nickname = True
    users_with_same_nickname = PortfolioUser.objects.filter(nickname=request.POST['nickname'])
    for user_with_same_nickname in users_with_same_nickname:
        if user.id is not user_with_same_nickname.id:
            data['error'] = "nickname already taken"
            valid_nickname = False
    if valid_nickname:
        user.nickname = request.POST['nickname']

    if is_valid_email(request.POST['email']):
        user.email = request.POST['email']
    else:
        data['error'] = "not a valid email address"

    if 'file' in request.FILES:
        user.avatar = request.FILES['file']
    user.save()
    data['nickname'] = user.nickname
    data['email'] = user.email
    return HttpResponse(json.dumps(data))


def is_valid_email(email):
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError

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