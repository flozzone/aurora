from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from Review.models import Review
from Challenge.models import Challenge

def create_context_review(request):
    data = {}
    if 'id' in request.GET:
        user=request.user
        challenge = Challenge.objects.get(pk=request.GET.get('id'))
    return data

@login_required()
def review(request):
    data = create_context_review(request)
    return render_to_response('review.html', data, context_instance=RequestContext(request))

@login_required()
def review_page(request):
    data = create_context_review(request)
    return render_to_response('review_page.html', data, context_instance=RequestContext(request))