from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from Challenge.models import Challenge
from Course.models import Course
from Elaboration.models import Elaboration
from PortfolioUser.models import PortfolioUser
from Stack.models import Stack, StackChallengeRelation
from Review.models import Review


@login_required()
def stack(request):
    data = create_stack_context(request)
    return render_to_response('stack.html', data, context_instance=RequestContext(request))


@login_required()
def stack_page(request):
    data = create_stack_context(request)
    return render_to_response('stack_page.html', data, context_instance=RequestContext(request))


def create_stack_context(request):
    data = {'reviews_per_challenge_range': range(3)}  # TODO: this should probably be defined somewhere else
    if 'id' in request.GET:
        stack = Stack.objects.get(pk=request.GET.get('id'))
        stack_challenges = StackChallengeRelation.objects.all().filter(stack=stack)
        challenges_active = []
        challenges_inactive = []
        for stack_challenge in stack_challenges:
            if stack_challenge.challenge.is_available_for_user(request.user):
                challenges_active.append({'challenge': stack_challenge.challenge, 'reviews': len(stack_challenge.challenge.get_reviews_written_by_user(request.user))})
            else:
                challenges_inactive.append(stack_challenge.challenge)
        data['challenges_active'] = challenges_active
        data['challenges_inactive'] = challenges_inactive
    return data


@login_required()
def challenges_page(request):
    data = {}
    gsi = Course.objects.get(short_title='gsi')
    course_stacks = Stack.objects.all().filter(course=gsi)
    data['course_stacks'] = course_stacks
    return render_to_response('challenges_page.html', data, context_instance=RequestContext(request))


@login_required()
def challenge(request):
    data = {}
    if 'id' in request.GET:
        print(request.GET.get('id'))
        challenge = Challenge.objects.get(pk=request.GET.get('id'))
        user = PortfolioUser.objects.get(id=request.user.id)
        data['challenge'] = challenge
        if Elaboration.objects.filter(challenge=challenge, user=user).exists():
            elaboration = Elaboration.objects.all().filter(challenge=challenge, user=user).order_by('id')[0]
            data['elaboration'] = elaboration
    return render_to_response('challenge.html', data, context_instance=RequestContext(request))