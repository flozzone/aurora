from django.shortcuts import render_to_response
from django.template import RequestContext


def challenges(request):
    return render_to_response('challenges.html', {}, context_instance=RequestContext(request))