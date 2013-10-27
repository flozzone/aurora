from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.utils import simplejson
from django.utils.timezone import utc
from Challenge.models import Challenge
from Course.models import Course
from Elaboration.models import Elaboration
from PortfolioUser.models import PortfolioUser
from Submission.models import Submission


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
        user = PortfolioUser.objects.get(id=request.user.id)
        data['challenge'] = challenge
        if Elaboration.objects.filter(challenge=challenge, user=user).exists():
            elaboration = Elaboration.objects.all().filter(challenge=challenge, user=user).order_by('id')[0]
            data['elaboration'] = elaboration
    return render_to_response('challenge_detail.html', data, context_instance=RequestContext(request))


@login_required()
def submit_challenge(request):
    print("here")

    if 'id' in request.GET:
        # todo: remove hardcoced course
        course = Course.objects.filter(short_title='gsi')
        challenge = Challenge.objects.get(id=request.GET['id'])
        user = PortfolioUser.objects.get(id=request.user.id)

        elaboration = Elaboration.objects.filter(challenge=challenge, user=user).latest('creationDate')

        try:
            submission = Submission.objects.get(elaboration=elaboration)
            submission.submissionState = Submission.SUBMISSION_STATE_WAITING_FOR_EVALUATION
            submission.submissionDate = Submission.submission_date.now(tz=utc)
            submission.save()

        except ObjectDoesNotExist:
            submission = Submission(elaboration=elaboration)
            submission.save()

    return HttpResponse()