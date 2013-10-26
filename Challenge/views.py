from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from Challenge.models import Challenge
from Course.models import Course


@login_required()
def challenges(request):
    return render_to_response('challenges.html', {}, context_instance=RequestContext(request))


@login_required()
def challenges_open(request):
    course_challenges = Course.getCourseChallenges('gsi')
    return render_to_response('challenges_open.html', {
        'challenges': course_challenges,
    }, context_instance=RequestContext(request))


@login_required()
def challenge_detail(request):
    data = {}
    if 'id' in request.GET:
        print(request.GET.get('id'))
        challenge = Challenge.objects.get(pk=request.GET.get('id'))
        data['challenge'] = challenge
    return render_to_response('challenge_detail.html', data, context_instance=RequestContext(request))
