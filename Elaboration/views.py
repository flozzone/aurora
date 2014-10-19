from datetime import datetime
from django.contrib.auth.tests import *
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from Challenge.models import Challenge
from Elaboration.models import Elaboration
from AuroraUser.models import AuroraUser
from Course.models import Course
from django.http import Http404
from FileUpload.models import UploadFile

@csrf_exempt
def save_elaboration(request):
    challenge_id = request.POST['challenge_id']
    elaboration_text = request.POST['elaboration_text']
    challenge = Challenge.objects.get(id=challenge_id)
    user = RequestContext(request)['user']
    if not challenge.is_enabled_for_user(user):
        raise Http404

    # check if elaboration exists
    if Elaboration.objects.filter(challenge=challenge, user=user).exists():
        elaboration = Elaboration.objects.all().filter(challenge=challenge, user=user).order_by('id').latest('creation_time')
        # only save if it is unsubmitted (because of js raise condition)
        if not elaboration.is_submitted():
            elaboration.elaboration_text = ''
            elaboration.elaboration_text = elaboration_text
            elaboration.save()
        else:
            raise Http404
    else:
        Elaboration.objects.get_or_create(challenge=challenge, user=user, elaboration_text=elaboration_text)

    return HttpResponse()

@login_required()
def create_elaboration(request):
    challenge_id = request.GET['id']
    challenge = Challenge.objects.get(id=challenge_id)
    user = RequestContext(request)['user']
    if not challenge.is_enabled_for_user(user):
        raise Http404
    elaboration, created = Elaboration.objects.get_or_create(user=user, challenge=challenge);
    if created:
        elaboration.elaboration_text = ""
        elaboration.save()
    return HttpResponse(elaboration.id)

# @login_required()
# def submit_elaboration(request):
#     if 'challenge_id' in request.POST:
#         challenge = Challenge.objects.get(id=request.POST['challenge_id'])
#         user = RequestContext(request)['user']
#         if not challenge.is_enabled_for_user(user):
#             raise Http404
#         if challenge.is_final_challenge() and challenge.is_in_lock_period(user,RequestContext(request)['last_selected_course']):
#             raise Http404
#         elaboration, created = Elaboration.objects.get_or_create(challenge=challenge, user=user)
#         elaboration.elaboration_text = request.POST['elaboration_text']
#         if elaboration.elaboration_text or UploadFile.objects.filter(elaboration=elaboration).exists():
#             elaboration.submission_time = datetime.now()
#             elaboration.save()
#             return HttpResponse()
#     raise Http404