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
    return render_to_response('evaluation.html', {}, context_instance=RequestContext(request))

@login_required()
def autocomplete_challenge(request):
    term = request.GET.get('term', '')
    challenges = Challenge.objects.all().filter(title__istartswith=term).order_by('title')
    titles = [challenge.title for challenge in challenges[:20]]
    json = simplejson.dumps(titles, ensure_ascii=False)
    return HttpResponse(json, mimetype='application/json; charset=utf-8')

@login_required()
def autocomplete_stack(request):
    term = request.GET.get('term', '')
    stacks = Stack.objects.all().filter(title__istartswith=term).order_by('title')
    titles = [stack.title for stack in stacks[:20]]
    json = simplejson.dumps(titles, ensure_ascii=False)
    return HttpResponse(json, mimetype='application/json; charset=utf-8')

@login_required()
def autocomplete_user(request):
    term = request.GET.get('term', '')
    pusers = PortfolioUser.objects.all().filter(nickname__istartswith=term).order_by('nickname')
    titles = [puser.nickname for puser in pusers[:20]]
    json = simplejson.dumps(titles, ensure_ascii=False)
    return HttpResponse(json, mimetype='application/json; charset=utf-8')

@login_required()
def search(request):
    if 'challenge_request' in request.GET:
        query = request.GET.get('challenge_request', '')
        results = Challenge.objects.all().filter(title__icontains=query).order_by('title')
    if 'stack_request' in request.GET:
        query = request.GET.get('stack_request', '')
        results = Stack.objects.all().filter(title__icontains=query).order_by('title')
    if 'user_request' in request.GET:
        query = request.GET.get('user_request', '')
        results = PortfolioUser.objects.all().filter(nickname__icontains=query).order_by('nickname')
    html = render_to_response('search.html', {'results': results})
    return html

@login_required()
def get_submission(request):
    if 'id' in request.GET:
        challenge_id = request.GET.get('id', '')
        challenge = Challenge.objects.get(pk=challenge_id)
        elaboration = Elaboration.objects.all().filter(challenge=challenge).order_by('id')[0]  # TODO: submission_time must be != null, check if elaboration exists
    html = render_to_response('submission.html', {'elaboration': elaboration})
    return html