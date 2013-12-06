from datetime import datetime
import json
from django.core import serializers
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from Challenge.models import Challenge
from Elaboration.models import Elaboration
from Evaluation.models import Evaluation
from PortfolioUser.models import PortfolioUser
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
    # store selected elaboration_id in session
    request.session['elaboration_id'] = elaboration.id

    reviews = Review.objects.filter(elaboration=elaboration)

    next = prev = None
    index = elaborations.index(elaboration)
    if index+1 < len(elaborations):
        next = elaborations[index+1].id
    if not index == 0:
        prev = elaborations[index-1].id

    stack_elaborations = elaboration.user.get_stack_elaborations(elaboration.challenge.get_stack())

    return render_to_response('detail.html',
        {'elaboration': elaboration,
         'stack_elaborations': stack_elaborations,
         'reviews': reviews,
         'next': next,
         'prev': prev
        }, RequestContext(request))

@login_required()
def stack(request):
    elaboration = Elaboration.objects.get(pk=request.session.get('elaboration_id', ''))
    stack_elaborations = elaboration.user.get_stack_elaborations(elaboration.challenge.get_stack())

    return render_to_response('user_stack.html', {'stack_elaborations': stack_elaborations}, RequestContext(request))

@login_required()
def others(request):
    # get selected elaborations from session
    elaboration = Elaboration.objects.get(pk=request.session.get('elaboration_id', ''))

    next = prev = None

    if elaboration.get_others():
        other_elaborations = elaboration.get_others()

        index=int(request.GET.get('page', '0'))
        elaboration_list = list(other_elaborations)

        if index+1 < len(elaboration_list):
            next = index+1
        if not index == 0:
            prev = index-1

        elaboration = elaboration_list[index]
    else:
        elaboration = []

    return render_to_response('others.html', {'elaboration': elaboration, 'next': next, 'prev': prev}, RequestContext(request))

@login_required()
def challenge_txt(request):
    elaboration = Elaboration.objects.get(pk=request.session.get('elaboration_id', ''))
    return render_to_response('challenge_txt.html', {'challenge': elaboration.challenge}, RequestContext(request))

@csrf_exempt
def save_evaluation(request):
    elaboration_id = request.POST['elaboration_id']
    evaluation_text = request.POST['evaluation_text']
    evaluation_points = request.POST['evaluation_points']

    print("autosaving evaluation...")
    elaboration = Elaboration.objects.get(pk=elaboration_id)

    if Evaluation.objects.filter(submission=elaboration, user=elaboration.user):
        evaluation = Evaluation.objects.filter(submission=elaboration, user=elaboration.user).order_by('id')[0]
    else:
        evaluation = Evaluation.objects.create(submission=elaboration, user=elaboration.user)

    if evaluation_text:
        evaluation.evaluation_text = evaluation_text
    if evaluation_points:
        evaluation.evaluation_points = evaluation_points
    evaluation.save()

    return HttpResponse()

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
    evaluation.submission_time = datetime.now()
    evaluation.save()

    return HttpResponse()

@csrf_exempt
def set_appraisal(request):
    review_id = request.POST['review_id']
    appraisal = request.POST['appraisal']

    review = Review.objects.get(pk=review_id)
    review.appraisal = appraisal
    review.save()

    return HttpResponse()

@csrf_exempt
@login_required()
def select_challenge(request):
    selected_challenge = request.POST['selected_challenge']

    elaborations = []
    challenge = Challenge.objects.get(title=selected_challenge)
    if Elaboration.get_sel_challenge_elaborations(challenge):
        elaborations = Elaboration.get_sel_challenge_elaborations(challenge)

    html = render_to_response('overview.html', {'elaborations': elaborations}, RequestContext(request))

    # store selected elaborations in session
    request.session['elaborations'] = serializers.serialize('json', elaborations)
    return html

@csrf_exempt
@login_required()
def search(request):
    search_user = request.POST['search_user']
    search_all = request.POST['search_all']

    elaborations = []
    if search_user not in ['', 'user...']:
        user = PortfolioUser.objects.get(username=search_user.split()[0])
        elaborations = user.get_elaborations()
    else:
        if search_all not in ['', 'all...']:
            print("todo...")

    html = render_to_response('overview.html', {'elaborations': elaborations}, RequestContext(request))

    # store selected elaborations in session
    request.session['elaborations'] = serializers.serialize('json', elaborations)
    return html

@login_required()
def autocomplete_challenge(request):
    term = request.GET.get('term', '')
    challenges = Challenge.objects.all().filter(title__istartswith=term)
    titles = [challenge.title for challenge in challenges[:20]]
    json = simplejson.dumps(titles, ensure_ascii=False)
    return HttpResponse(json, mimetype='application/json; charset=utf-8')

@login_required()
def autocomplete_user(request):
    term = request.GET.get('term', '')
    studies = PortfolioUser.objects.all().filter(
        Q(username__istartswith=term) | Q(first_name__istartswith=term) | Q(last_name__istartswith=term))
    names = [(studi.username + ' ' + studi.first_name + ' ' + studi.last_name) for studi in studies[:20]]
    json = simplejson.dumps(names, ensure_ascii=False)
    return HttpResponse(json, mimetype='application/json; charset=utf-8')

@login_required()
def autocomplete_all(request):
    term = request.GET.get('term', '')
    studies = PortfolioUser.objects.all().filter(
        Q(username__istartswith=term) | Q(first_name__istartswith=term) | Q(last_name__istartswith=term))
    names = [studi.username for studi in studies[:20]]
    json = simplejson.dumps(names, ensure_ascii=False)
    return HttpResponse(json, mimetype='application/json; charset=utf-8')