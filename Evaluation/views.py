from django.http import HttpResponse
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.utils import simplejson
from Challenge.models import Challenge
from PortfolioUser.models import PortfolioUser
from Stack.models import Stack
from Elaboration.models import Elaboration


@login_required()
def evaluation(request):
    challenges = Challenge.objects.all()
    return render_to_response('evaluation.html', {'challenges': challenges}, context_instance=RequestContext(request))

@login_required()
def submission(request):
    if 'challenge_id' in request.GET:
        challenge_id = request.GET.get('challenge_id', '')
        challenge = Challenge.objects.get(pk=challenge_id)

        elaborations = challenge.get_submissions()
        html = render_to_response('submission.html', {'elaborations': elaborations})
        return html