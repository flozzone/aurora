from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from Course.models import Course

@login_required()
def challenges(request):
    return render_to_response('challenges.html', {}, context_instance=RequestContext(request))

def challenges_open(request):
    challenges = Course.getCourseChallenges('gsi')
    return render_to_response('challenges_open.html', {
        'challenges': challenges,
    }, context_instance=RequestContext(request))