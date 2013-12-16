import json
from django.core.files import File
from django.http import HttpResponse
from django.contrib.auth import authenticate, login as django_login, logout
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from PortfolioUser.models import PortfolioUser


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