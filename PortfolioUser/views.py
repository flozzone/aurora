import json
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout


def signin(request):
    if request.method == 'POST':

        if not request.POST.get('remember', None):
            request.session.set_expiry(0)

        if 'username' in request.POST and 'password' in request.POST:
            username = request.POST['username']
            password = request.POST['password']
            print(username)
            print(password)

            user = authenticate(username=username, password=password)

            if user is not None:
                if user.is_active:
                    login(request, user)
                    response_data = {'success': True}
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