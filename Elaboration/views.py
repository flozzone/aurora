from datetime import datetime
from django.contrib.auth.tests import *
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from Challenge.models import Challenge
from Elaboration.models import Elaboration
from PortfolioUser.models import PortfolioUser
from Course.models import Course

@csrf_exempt
def save_elaboration(request):
    challenge_id = request.POST['challenge_id']
    elaboration_text = request.POST['elaboration_text']
    challenge = Challenge.objects.get(id=challenge_id)
    user = RequestContext(request)['user']

    # check if elaboration exists
    if Elaboration.objects.filter(challenge=challenge, user=user).exists():
        elaboration = Elaboration.objects.all().filter(challenge=challenge, user=user).order_by('id').latest('creation_time')
        elaboration.elaboration_text = ''
        elaboration.elaboration_text = elaboration_text
        elaboration.save()
    else:
        elaboration = Elaboration.objects.create(challenge=challenge, user= user, elaboration_text=elaboration_text)

    return HttpResponse()

@login_required()
def create_elaboration(request):
    challenge_id = request.GET['id']
    challenge = Challenge.objects.get(id=challenge_id)
    user = RequestContext(request)['user']
    elaboration, created = Elaboration.objects.get_or_create(user=user, challenge=challenge);
    if created:
        elaboration.elaboration_text = ""
        elaboration.save()
    return HttpResponse(elaboration.id)

@login_required()
def submit_elaboration(request):
    if 'id' in request.GET:
        course = RequestContext(request)['last_selected_course']
        challenge = Challenge.objects.get(id=request.GET['id'])
        user = RequestContext(request)['user']
        elaboration, created = Elaboration.objects.get_or_create(challenge=challenge, user=user)
        elaboration.submission_time = datetime.now()
        elaboration.save()
    return HttpResponse()