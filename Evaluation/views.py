from datetime import datetime
import json

from django.core import serializers
from django.db.models import TextField
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.db.models import CharField
from django.db.models import Q
from django.db import models

from Challenge.models import Challenge
from Comments.models import Comment
from Course.models import Course, CourseChallengeRelation
from Elaboration.models import Elaboration
from Evaluation.models import Evaluation
from PortfolioUser.models import PortfolioUser
from Review.models import Review
from ReviewAnswer.models import ReviewAnswer
from ReviewQuestion.models import ReviewQuestion
from Stack.models import Stack
from Notification.models import Notification


@login_required()
def evaluation(request):
    # TODO: delete this snippet, fetches gravatar images for every user only for test cases.
    for puser in PortfolioUser.objects.all():
        if not puser.avatar:
            puser.get_gravatar()

    overview = ""
    if request.session.get('selection'):
        elaborations = []
        for serialized_elaboration in serializers.deserialize('json', request.session.get('elaborations', {})):
            elaborations.append(serialized_elaboration.object)
        overview = render_to_string('overview.html', {'elaborations': elaborations})

    challenges = Challenge.objects.all()
    return render_to_response('evaluation.html',
                              {'challenges': challenges,
                               'missing_reviews': Elaboration.get_missing_reviews(),
                               'top_level_challenges': Elaboration.get_top_level_challenges(),
                               'non_adequate_work': Elaboration.get_non_adequate_work(),
                               'evaluated_non_adequate_work': Elaboration.get_evaluated_non_adequate_work(),
                               'complaints': Elaboration.get_complaints(RequestContext(request)),
                               'questions': Challenge.get_questions(RequestContext(request)),
                               'awesome': Elaboration.get_awesome(),
                               'overview': overview,
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
    if request.GET.get('data', '') == "top_level_challenges":
        print("loading top level challenges...")
        elaborations = Elaboration.get_top_level_challenges()
    if request.GET.get('data', '') == "non_adequate_work":
        print("loading non adequate work...")
        elaborations = Elaboration.get_non_adequate_work()
    if request.GET.get('data', '') == "complaints":
        print("loading complaints...")
        elaborations = Elaboration.get_complaints(RequestContext(request))
    if request.GET.get('data', '') == "awesome":
        print("loading awesome work...")
        elaborations = Elaboration.get_awesome()
    if request.GET.get('data', '') == "evaluated_non_adequate_work":
        print("loading evaluated non adequate work...")
        elaborations = Elaboration.get_evaluated_non_adequate_work()

    # sort elaborations by submission time
    elaborations.sort(key=lambda elaboration: elaboration.submission_time)

    # store selected elaborations in session
    request.session['elaborations'] = serializers.serialize('json', elaborations)
    request.session['selection'] = request.GET.get('data', '')

    html = render_to_response('overview.html', {'elaborations': elaborations}, RequestContext(request))
    return html


@login_required()
def questions(request):
    print("loading questions...")
    challenges = Challenge.get_questions(RequestContext(request))
    html = render_to_response('questions.html', {'challenges': challenges}, RequestContext(request))
    return html


@login_required()
def detail(request):
    # get selected elaborations from session
    elaborations = []
    params = {}
    for serialized_elaboration in serializers.deserialize('json', request.session.get('elaborations', {})):
        elaborations.append(serialized_elaboration.object)
    selection = request.session.get('selection', 'error')

    if not 'elaboration_id' in request.GET:
        return False;

    elaboration = Elaboration.objects.get(pk=request.GET.get('elaboration_id', ''))
    # store selected elaboration_id in session
    request.session['elaboration_id'] = elaboration.id

    if selection == "missing_reviews":
        print('selection: missing_reviews')
        questions = ReviewQuestion.objects.filter(challenge=elaboration.challenge).order_by("order")
        params = {'questions': questions}
    if selection == "top_level_challenges":
        # set evaluation lock
        user = RequestContext(request)['user']
        lock = False
        if Evaluation.objects.filter(submission=elaboration):
            evaluation = Evaluation.objects.get(submission=elaboration)
            if evaluation.tutor == user:
                evaluation.lock_time = datetime.now()
                evaluation.save()
            else:
                if evaluation.is_older_15min():
                    evaluation.lock_time = datetime.now()
                    evaluation.tutor = user
                    evaluation.save()
                else:
                    lock = True
        else:
            evaluation = Evaluation.objects.create(submission=elaboration, tutor=user)
            evaluation.lock_time = datetime.now()
            evaluation.save()
        params = {'evaluation': evaluation, 'lock': lock}
    if selection == "non_adequate_work":
        print('selection: non_adequate_work')
        params = {}
    if selection == "non_adequate_reviews":
        print('selection: non_adequate_reviews')
        params = {}
    if selection == "complaints":
        print('selection: complaints')
        params = {}
    if selection == "awesome":
        print('selection: awesome')
        params = {}
    if selection == "evaluated_non_adequate_work":
        print('selection: evaluated_non_adequate_work')
        params = {}
    if selection == "search":
        if elaboration.challenge.is_final_challenge():
            if Evaluation.objects.filter(submission=elaboration):
                evaluation = Evaluation.objects.get(submission=elaboration)
                params = {'evaluation': evaluation}

    reviews = Review.objects.filter(elaboration=elaboration)

    next = prev = None
    index = elaborations.index(elaboration)
    if index + 1 < len(elaborations):
        next = elaborations[index + 1].id
    if not index == 0:
        prev = elaborations[index - 1].id

    stack_elaborations = elaboration.user.get_stack_elaborations(elaboration.challenge.get_stack())
    # sort stack_elaborations by submission time
    stack_elaborations.sort(key=lambda stack_elaboration: stack_elaboration.submission_time)

    params['elaboration'] = elaboration
    params['stack_elaborations'] = stack_elaborations
    params['reviews'] = reviews
    params['next'] = next
    params['prev'] = prev
    params['selection'] = selection

    return render_to_response('detail.html', params, RequestContext(request))


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

        index = int(request.GET.get('page', '0'))
        elaboration_list = list(other_elaborations)

        if index + 1 < len(elaboration_list):
            next = index + 1
        if not index == 0:
            prev = index - 1

        elaboration = elaboration_list[index]
    else:
        elaboration = []

    return render_to_response('others.html', {'elaboration': elaboration, 'next': next, 'prev': prev},
                              RequestContext(request))


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
    evaluation = Evaluation.objects.get(submission=elaboration)

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
    user = RequestContext(request)['user']
    course = CourseChallengeRelation.objects.filter(challenge=elaboration.challenge)[0].course

    if Evaluation.objects.filter(submission=elaboration):
        evaluation = Evaluation.objects.get(submission=elaboration)
    else:
        evaluation = Evaluation.objects.create(submission=elaboration)

    evaluation.user = user = user
    evaluation.evaluation_text = evaluation_text
    evaluation.evaluation_points = evaluation_points
    evaluation.submission_time = datetime.now()
    evaluation.save()
    obj, created = Notification.objects.get_or_create(
        user=elaboration.user,
        course=course,
        text=Notification.SUBMISSION_EVALUATED + elaboration.challenge.title,
        image_url= elaboration.challenge.image.url,
        link="stack=" + str(elaboration.challenge.get_stack().id)
    )
    obj.read = False
    obj.save
    return HttpResponse()


@csrf_exempt
def reopen_evaluation(request):
    elaboration_id = request.POST['elaboration_id']
    elaboration = Elaboration.objects.get(pk=elaboration_id)
    evaluation = Evaluation.objects.get(submission=elaboration)
    course = CourseChallengeRelation.objects.filter(challenge=evaluation.submission.challenge)[0].course

    evaluation.submission_time = None
    evaluation.save()

    obj, created = Notification.objects.get_or_create(
        user=evaluation.submission.user,
        course=course,
        text=Notification.SUBMISSION_EVALUATED + evaluation.submission.challenge.title,
        image_url=evaluation.submission.challenge.image.url,
        link="stack=" + str(evaluation.submission.challenge.get_stack().id)
    )
    obj.creation_time = datetime.now()
    obj.read = False
    obj.save()
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
    request.session['selection'] = 'search'
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
    if search_all not in ['', 'all...']:
        SEARCH_TERM = search_all

        for md in models.get_models():
            # search query in all models and fields (char and textfields) of database
            fields = [f for f in md._meta.fields if isinstance(f, CharField) or isinstance(f, TextField)]
            if fields:
                queries = [Q(**{f.name + '__icontains': SEARCH_TERM}) for f in fields]

                qs = Q()
                for query in queries:
                    qs = qs | query

                results = md.objects.filter(qs)
                for result in results:
                    if isinstance(result, PortfolioUser):
                        print("PortfolioUser: ", result)
                        for elaboration in result.get_elaborations():
                            if elaboration not in elaborations:
                                elaborations.append(elaboration)
                    if isinstance(result, Elaboration):
                        print("Elaboration: ", result)
                        if result not in elaborations:
                            elaborations.append(result)
                    if isinstance(result, Challenge):
                        print("Challenge: ", result)
                        if Elaboration.get_sel_challenge_elaborations(result):
                            for elaboration in Elaboration.get_sel_challenge_elaborations(result):
                                if elaboration not in elaborations:
                                    elaborations.append(elaboration)
                    if isinstance(result, Course):
                        print("Course: ", result)
                        for elaboration in Elaboration.get_course_elaborations(result):
                            if elaboration not in elaborations:
                                elaborations.append(elaboration)
                    if isinstance(result, Stack):
                        print("Stack: ", result)
                        for elaboration in Elaboration.get_stack_elaborations(result):
                            if elaboration not in elaborations:
                                elaborations.append(elaboration)
                    if isinstance(result, Evaluation):
                        print("Evaluation: ", result)
                        if result.submission not in elaborations:
                            elaborations.append(result.submission)
                    if isinstance(result, Review):
                        print("Review: ", result)
                        if result.elaboration not in elaborations:
                            elaborations.append(result.elaboration)
                    if isinstance(result, ReviewAnswer):
                        print("ReviewAnswer: ", result)
                    if isinstance(result, ReviewQuestion):
                        print("ReviewQuestion: ", result)
                    if isinstance(result, Comment):
                        print("Comments: ", result)

    html = render_to_response('overview.html', {'elaborations': elaborations}, RequestContext(request))

    # store selected elaborations in session
    request.session['elaborations'] = serializers.serialize('json', elaborations)
    request.session['selection'] = 'search'
    return html


@login_required()
def autocomplete_challenge(request):
    term = request.GET.get('term', '')
    challenges = Challenge.objects.all().filter(title__istartswith=term)
    titles = [challenge.title for challenge in challenges]
    response_data = json.dumps(titles, ensure_ascii=False)
    return HttpResponse(response_data, mimetype='application/json; charset=utf-8')


@login_required()
def autocomplete_user(request):
    term = request.GET.get('term', '')
    studies = PortfolioUser.objects.all().filter(
        Q(username__istartswith=term) | Q(first_name__istartswith=term) | Q(last_name__istartswith=term))
    names = [(studi.username + ' ' + studi.first_name + ' ' + studi.last_name) for studi in studies]
    response_data = json.dumps(names, ensure_ascii=False)
    return HttpResponse(response_data, mimetype='application/json; charset=utf-8')


@login_required()
def load_reviews(request):
    if not 'elaboration_id' in request.GET:
        return False;

    elaboration = Elaboration.objects.get(pk=request.GET.get('elaboration_id', ''))
    reviews = Review.objects.filter(elaboration=elaboration)

    return render_to_response('stack_rev.html', {'elaboration': elaboration, 'reviews': reviews, 'stack': 'stack'},
                              RequestContext(request))


@csrf_exempt
@login_required()
def review_answer(request):
    if request.POST:
        data = request.body.decode(encoding='UTF-8')
        data = json.loads(data)
        user = RequestContext(request)['user']
        answers = data['answers']
        review = Review.objects.create(elaboration_id=request.session.get('elaboration_id', ''), reviewer_id=user.id)
        review.appraisal = data['appraisal']
        review.submission_time = datetime.now()
        review.save()
        for answer in answers:
            print("question id: ", answer['question_id'])
            question_id = answer['question_id']
            text = answer['answer']
            review_question = ReviewQuestion.objects.get(pk=question_id)
            ReviewAnswer(review=review, review_question=review_question, text=text).save()
    return HttpResponse()