import json
from django.core import serializers
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from Challenge.models import Challenge
from Elaboration.models import Elaboration
from Evaluation.models import Evaluation
from Review.models import Review


@login_required()
def evaluation(request):
    challenges = Challenge.objects.all()
    return render_to_response('evaluation.html',
            {'challenges': challenges,
             'missing_reviews': Elaboration.get_missing_reviews(),
             'top_level_challenges': Elaboration.get_top_level_challenges(),
             'non_adequate_work': Elaboration.get_non_adequate_work()
            },
            context_instance=RequestContext(request))

@login_required()
def overview(request):
    challenges = Challenge.objects.all()
    missing_reviews = Elaboration.get_missing_reviews()
    return render_to_response('overview.html',
            {'challenges': challenges,
             'missing_reviews': missing_reviews
            },
            context_instance=RequestContext(request))

@login_required()
def update_overview(request):
    if request.GET.get('data', '') == "missing_reviews":
        print("loading missing reviews...")
        elaborations = Elaboration.get_missing_reviews()
        html = render_to_response('overview.html', {'elaborations': elaborations}, RequestContext(request))
    if request.GET.get('data', '') == "top_level_challenges":
        print("loading top level challenges...")
        elaborations = Elaboration.get_top_level_challenges()
        html = render_to_response('overview.html', {'elaborations': elaborations}, RequestContext(request))
    if request.GET.get('data', '') == "non_adequate_work":
        print("loading non adequate work...")
        elaborations = Elaboration.get_non_adequate_work()
        html = render_to_response('overview.html', {'elaborations': elaborations}, RequestContext(request))

    # store selected elaborations in session
    request.session['elaborations'] = serializers.serialize('json', elaborations)
    return html

@login_required()
def detail(request):
    # get selected elaborations from session
    elaborations = []
    for serialized_elaboration in serializers.deserialize('json', request.session.get('elaborations', {})):
        elaborations.append(serialized_elaboration.object)

    if not 'elaboration_id' in request.GET:
        return False;

    elaboration = Elaboration.objects.get(pk=request.GET.get('elaboration_id', ''))
    reviews = Review.objects.filter(elaboration=elaboration)

    next = prev = None
    index = elaborations.index(elaboration)
    if index+1 < len(elaborations):
        next = elaborations[index+1].id
    if not index == 0:
        prev = elaborations[index-1].id

    return render_to_response('detail.html',
        {'elaboration': elaboration,
         'elaborations': elaborations,
         'reviews': reviews,
         'next': next,
         'prev': prev
        }, RequestContext(request))

@csrf_exempt
def submit_evaluation(request):
    elaboration_id = request.POST['elaboration_id']
    evaluation_text = request.POST['evaluation_text']
    evaluation_points = request.POST['evaluation_points']

    elaboration = Elaboration.objects.get(pk=elaboration_id)

    if Evaluation.objects.filter(submission=elaboration, user=elaboration.user):
        evaluation = Evaluation.objects.filter(submission=elaboration, user=elaboration.user).order_by('id')[0]
    else:
        evaluation = Evaluation.objects.create(submission=elaboration, user=elaboration.user)

    evaluation.evaluation_text = evaluation_text
    evaluation.evaluation_points = evaluation_points
    evaluation.save()

    return HttpResponse()