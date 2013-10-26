from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required



@login_required()
def challenges(request):
    return render_to_response('elaboration.html', {}, context_instance=RequestContext(request))