from django.http import HttpResponse
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.utils import simplejson
from Challenge.models import Challenge


@login_required()
def evaluation(request):
    return render_to_response('evaluation.html', {}, context_instance=RequestContext(request))

@login_required()
def autocomplete(request):
    term = request.GET.get('term', '')
    challenges = Challenge.objects.all().filter(title__istartswith=term).order_by('title')
    titles = [challenge.title for challenge in challenges[:20]]
    json = simplejson.dumps(titles, ensure_ascii=False)
    return HttpResponse(json, mimetype='application/json; charset=utf-8')

@login_required()
def search(request):
    query = request.GET.get('request', '')
    results = Challenge.objects.all().filter(title__icontains=query).order_by('title')
    return render(request, 'search.html', {'results': results})