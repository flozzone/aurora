import json
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from Challenge.models import Challenge
from Elaboration.models import Elaboration
from Evaluation.models import Evaluation


@login_required()
def evaluation(request):
    challenges = Challenge.objects.all()
    waiting_elaborations = Elaboration.get_waiting_elaborations()
    return render_to_response('evaluation.html', {'challenges': challenges, 'waiting_elaborations': waiting_elaborations}, context_instance=RequestContext(request))

@login_required()
def submission(request):
    if 'challenge_id' in request.GET:
        challenge_id = request.GET.get('challenge_id', '')
        challenge = Challenge.objects.get(pk=challenge_id)

        elaboration_list = challenge.get_submissions()

        paginator = Paginator(elaboration_list, 1)              # elaborations per page

        page = request.GET.get('page')
        try:
            elaborations = paginator.page(page)
        except PageNotAnInteger:
            elaborations = paginator.page(1)                    # first page
        except EmptyPage:
            elaborations = paginator.page(paginator.num_pages)  # last page

        html = render_to_response('submission.html', {'elaborations': elaborations, 'challenge': challenge}, RequestContext(request))
    return html

@login_required()
def waiting(request):
    elaboration_list = Elaboration.get_waiting_elaborations()
    paginator = Paginator(elaboration_list, 1)              # elaborations per page

    page = request.GET.get('page')
    try:
        elaborations = paginator.page(page)
    except PageNotAnInteger:
        elaborations = paginator.page(1)                    # first page
    except EmptyPage:
        elaborations = paginator.page(paginator.num_pages)  # last page

    html = render_to_response('waiting.html', {'elaborations': elaborations})

    return html

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