from datetime import datetime
from difflib import SequenceMatcher
import difflib
import json
from django.contrib.contenttypes.models import ContentType

from django.core import serializers
from django.db.models import TextField
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.db.models import CharField
from django.db.models import Q
from django.db import models

from Challenge.models import Challenge
from Comments.models import Comment
from Course.models import Course, CourseUserRelation
from Elaboration.models import Elaboration
from Evaluation.models import Evaluation
from AuroraUser.models import AuroraUser
from Review.models import Review
from ReviewAnswer.models import ReviewAnswer
from ReviewQuestion.models import ReviewQuestion
from Stack.models import Stack
from Notification.models import Notification


@login_required()
@staff_member_required
def evaluation(request, course_short_title=None):
    course = Course.get_or_raise_404(short_title=course_short_title)
    overview = ""
    elaborations = []
    count = 0
    selection = request.session.get('selection', 'error')
    if selection not in ('error', 'questions'):
        for serialized_elaboration in serializers.deserialize('json', request.session.get('elaborations', {})):
            elaborations.append(serialized_elaboration.object)
        if selection == 'search':
            if 'id' in request.GET:
                points = get_points(request, AuroraUser.objects.get(pk=request.GET['id']))
                data = {'elaborations': elaborations, 'search': True, 'stacks': points['stacks'],
                        'courses': points['courses'], 'course': course}
            else:
                data = {'elaborations': elaborations, 'search': True, 'course': course}
        else:
            data = {'elaborations': elaborations, 'course': course}
        overview = render_to_string('overview.html', data, RequestContext(request))
        count = len(elaborations)
    elif selection == 'questions':
        # get selected challenges from session
        challenges = []
        for serialized_challenge in serializers.deserialize('json', request.session.get('challenges', {})):
            challenges.append(serialized_challenge.object)
        count = len(challenges)
        overview = render_to_string('questions.html', {'challenges': challenges}, RequestContext(request))

    challenges = Challenge.objects.all()

    return render_to_response('evaluation.html',
                              {'challenges': challenges,
                               'count_' + request.session.get('selection', ''): request.session.get('count', ''),
                               'stabilosiert_' + request.session.get('selection', ''): 'stabilosiert',
                               'overview': overview,
                               'count_' + request.session.get('selection', ''): count,
                               'stabilosiert_' + request.session.get('selection', ''): 'stabilosiert',
                               'course': course
                              },
                              context_instance=RequestContext(request))


@login_required()
@staff_member_required
def missing_reviews(request, course_short_title=None):
    course = Course.get_or_raise_404(short_title=course_short_title)
    elaborations = Elaboration.get_missing_reviews(course)

    # sort elaborations by submission time
    if type(elaborations) == list:
        elaborations.sort(key=lambda elaboration: elaboration.submission_time)
    else:
        elaborations.order_by('submission_time')

    # store selected elaborations in session
    request.session['elaborations'] = serializers.serialize('json', elaborations)
    request.session['selection'] = 'missing_reviews'
    request.session['count'] = len(elaborations)

    return render_to_response('evaluation.html',
                              {'overview': render_to_string('overview.html', {'elaborations': elaborations, 'course': course},
                                                            RequestContext(request)),
                               'count_missing_reviews': request.session.get('count', '0'),
                               'stabilosiert_missing_reviews': 'stabilosiert',
                               'selection': request.session['selection'],
                               'course': course
                              },
                              context_instance=RequestContext(request))


@login_required()
@staff_member_required
def non_adequate_work(request, course_short_title=None):
    course = Course.get_or_raise_404(short_title=course_short_title)
    elaborations = Elaboration.get_non_adequate_work(course)

    # sort elaborations by submission time
    if type(elaborations) == list:
        elaborations.sort(key=lambda elaboration: elaboration.submission_time)
    else:
        elaborations.order_by('submission_time')

    # store selected elaborations in session
    request.session['elaborations'] = serializers.serialize('json', elaborations)
    request.session['selection'] = 'non_adequate_work'
    request.session['count'] = len(elaborations)

    return render_to_response('evaluation.html',
                              {'overview': render_to_string('overview.html', {'elaborations': elaborations, 'course': course},
                                                            RequestContext(request)),
                               'count_non_adequate_work': request.session.get('count', '0'),
                               'stabilosiert_non_adequate_work': 'stabilosiert',
                               'selection': request.session['selection'],
                               'course': course
                              },
                              context_instance=RequestContext(request))


@login_required()
@staff_member_required
def top_level_tasks(request, course_short_title=None):
    course = Course.get_or_raise_404(short_title=course_short_title)
    elaborations = Elaboration.get_top_level_challenges(course)

    # sort elaborations by submission time
    if type(elaborations) == list:
        elaborations.sort(key=lambda elaboration: elaboration.submission_time)
    else:
        elaborations.order_by('submission_time')

    # store selected elaborations in session
    request.session['elaborations'] = serializers.serialize('json', elaborations)
    request.session['selection'] = 'top_level_challenges'
    request.session['count'] = len(elaborations)

    return render_to_response('evaluation.html',
                              {'overview': render_to_string('overview.html', {'elaborations': elaborations, 'course': course},
                                                            RequestContext(request)),
                               'count_top_level_tasks': request.session.get('count', '0'),
                               'stabilosiert_top_level_tasks': 'stabilosiert',
                               'selection': request.session['selection'],
                               'course': course
                              },
                              context_instance=RequestContext(request))


@login_required()
@staff_member_required
def complaints(request, course_short_title=None):
    course = Course.get_or_raise_404(short_title=course_short_title)
    elaborations = Elaboration.get_complaints(RequestContext(request), course)

    # sort elaborations by submission time
    if type(elaborations) == list:
        elaborations.sort(key=lambda elaboration: elaboration.submission_time)
    else:
        elaborations.order_by('submission_time')

    # store selected elaborations in session
    request.session['elaborations'] = serializers.serialize('json', elaborations)
    request.session['selection'] = 'complaints'
    request.session['count'] = len(elaborations)

    return render_to_response('evaluation.html',
                              {'overview': render_to_string('overview.html', {'elaborations': elaborations, 'course': course},
                                                            RequestContext(request)),
                               'count_complaints': request.session.get('count', '0'),
                               'stabilosiert_complaints': 'stabilosiert',
                               'selection': request.session['selection'],
                               'course': course
                              },
                              context_instance=RequestContext(request))


@login_required()
@staff_member_required
def evaluated_non_adequate_work(request, course_short_title=None):
    course = Course.get_or_raise_404(short_title=course_short_title)
    elaborations = Elaboration.get_evaluated_non_adequate_work(course)

    # sort elaborations by submission time
    if type(elaborations) == list:
        elaborations.sort(key=lambda elaboration: elaboration.submission_time)
    else:
        elaborations.order_by('submission_time')

    # store selected elaborations in session
    request.session['elaborations'] = serializers.serialize('json', elaborations)
    request.session['selection'] = 'evaluated_non_adequate_work'
    request.session['count'] = len(elaborations)

    return render_to_response('evaluation.html',
                              {'overview': render_to_string('overview.html', {'elaborations': elaborations, 'course': course},
                                                            RequestContext(request)),
                               'count_evaluated_non_adequate_work': request.session.get('count', '0'),
                               'stabilosiert_evaluated_non_adequate_work': 'stabilosiert',
                               'selection': request.session['selection'],
                               'course': course
                              },
                              context_instance=RequestContext(request))


@login_required()
@staff_member_required
def awesome(request, course_short_title=None):
    course = Course.get_or_raise_404(short_title=course_short_title)
    selected_challenge = request.session.get('selected_challenge', default='')
    if selected_challenge != '':
        challenge = Challenge.objects.get(title=selected_challenge, course=course)
        elaborations = Elaboration.get_awesome_challenge(course, challenge)
    else:
        elaborations = Elaboration.get_awesome(course)

    # sort elaborations by submission time
    if type(elaborations) == list:
        elaborations.sort(key=lambda elaboration: elaboration.submission_time)
    else:
        elaborations.order_by('submission_time')

    # store selected elaborations in session
    request.session['elaborations'] = serializers.serialize('json', elaborations)
    request.session['selection'] = 'awesome'
    request.session['selected_challenge'] = ''
    request.session['count'] = len(elaborations)

    return render_to_response('evaluation.html',
                              {'overview': render_to_string('overview.html', {'elaborations': elaborations, 'course': course},
                                                            RequestContext(request)),
                               'count_awesome': request.session.get('count', '0'),
                               'selected_challenge': selected_challenge,
                               'stabilosiert_awesome': 'stabilosiert',
                               'selection': request.session['selection'],
                               'course': course
                              },
                              context_instance=RequestContext(request))


@login_required()
@staff_member_required
def questions(request, course_short_title=None):
    challenges = Challenge.get_questions(RequestContext(request))
    course = Course.get_or_raise_404(short_title=course_short_title)

    # store selected challenges in session
    request.session['challenges'] = serializers.serialize('json', challenges)

    # store selected elaborations in session
    elaborations = []
    request.session['elaborations'] = elaborations
    request.session['selection'] = 'questions'
    request.session['count'] = len(challenges)

    return render_to_response('evaluation.html',
                              {'challenges': challenges,
                               'overview': render_to_string('overview.html', {'elaborations': elaborations, 'course': course},
                                                            RequestContext(request)),
                               'count_questions': request.session.get('count', '0'),
                               'stabilosiert_questions': 'stabilosiert',
                               'selection': request.session['selection'],
                               'course': course
                              },
                              context_instance=RequestContext(request))


@login_required()
@staff_member_required
def detail(request, course_short_title=None):
    course = Course.get_or_raise_404(short_title=course_short_title)

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
        questions = ReviewQuestion.objects.filter(challenge=elaboration.challenge).order_by("order")
        params = {'questions': questions, 'selection': 'missing reviews'}
    if selection == "top_level_challenges":
        evaluation = None
        user = RequestContext(request)['user']
        lock = False
        if Evaluation.objects.filter(submission=elaboration):
            evaluation = Evaluation.objects.get(submission=elaboration)
            if evaluation.tutor != user and not evaluation.is_older_15min():
                lock = True
        params = {'evaluation': evaluation, 'lock': lock, 'selection': 'top-level tasks'}
    if selection == "non_adequate_work":
        params = {'selection': 'non-adequate work'}
    if selection == "complaints":
        if elaboration.challenge.is_final_challenge():
            evaluation = None
            user = RequestContext(request)['user']
            lock = False
            if Evaluation.objects.filter(submission=elaboration):
                evaluation = Evaluation.objects.get(submission=elaboration)
                if evaluation.tutor != user and not evaluation.is_older_15min():
                    lock = True
            params = {'evaluation': evaluation, 'lock': lock, 'selection': 'complaints'}
        else:
            params = {'selection': 'complaints'}
    if selection == "awesome":
        params = {'selection': 'awesome'}
    if selection == "evaluated_non_adequate_work":
        params = {'selection': 'evaluated non-adequate work'}
    if selection == "search":
        evaluation = None
        user = RequestContext(request)['user']
        lock = False
        if Evaluation.objects.filter(submission=elaboration):
            evaluation = Evaluation.objects.get(submission=elaboration)
            if evaluation.tutor != user and not evaluation.is_older_15min():
                lock = True
        params = {'evaluation': evaluation, 'lock': lock}

    reviews = Review.objects.filter(elaboration=elaboration, submission_time__isnull=False)

    next = prev = None
    index = elaborations.index(elaboration)
    if index + 1 < len(elaborations):
        next = elaborations[index + 1].id
    if not index == 0:
        prev = elaborations[index - 1].id

    stack_elaborations = elaboration.user.get_stack_elaborations(elaboration.challenge.get_stack())
    # sort stack_elaborations by submission time
    if type(stack_elaborations) == list:
        stack_elaborations.sort(key=lambda stack_elaboration: stack_elaboration.submission_time)
    else:
        stack_elaborations.order_by('submission_time')

    params['elaboration'] = elaboration
    params['stack_elaborations'] = stack_elaborations
    params['reviews'] = reviews
    params['next'] = next
    params['prev'] = prev
    params['course'] = course

    detail_html = render_to_string('detail.html', params, RequestContext(request))

    challenges = Challenge.objects.all()
    return render_to_response('evaluation.html', {'challenges': challenges, 'course': course, 'detail_html': detail_html},
                              context_instance=RequestContext(request))



@login_required()
@staff_member_required
def start_evaluation(request, course_short_title=None):
    if not 'elaboration_id' in request.GET:
        return False;

    elaboration = Elaboration.objects.get(pk=request.GET.get('elaboration_id', ''))

    # set evaluation lock
    state = 'open'
    user = RequestContext(request)['user']
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
                state = 'locked by ' + evaluation.tutor.username
    else:
        evaluation = Evaluation.objects.create(submission=elaboration, tutor=user)
        evaluation.lock_time = datetime.now()
        evaluation.save()
        state = 'init'

    return HttpResponse(state)


@login_required()
@staff_member_required
def stack(request, course_short_title=None):
    elaboration = Elaboration.objects.get(pk=request.session.get('elaboration_id', ''))
    stack_elaborations = elaboration.user.get_stack_elaborations(elaboration.challenge.get_stack())

    return render_to_response('tasks.html', {'stack_elaborations': stack_elaborations}, RequestContext(request))


@login_required()
@staff_member_required
def others(request, course_short_title=None):
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

    evaluation = None
    if elaboration.challenge.is_final_challenge():
        if Evaluation.objects.filter(submission=elaboration, submission_time__isnull=False):
            evaluation = Evaluation.objects.get(submission=elaboration, submission_time__isnull=False)

    return render_to_response('others.html',
                              {'elaboration': elaboration, 'evaluation': evaluation, 'next': next, 'prev': prev},
                              RequestContext(request))


@login_required()
@staff_member_required
def challenge_txt(request, course_short_title=None):
    elaboration = Elaboration.objects.get(pk=request.session.get('elaboration_id', ''))
    return render_to_response('challenge_txt.html',
                              {'challenge': elaboration.challenge, 'stack': elaboration.challenge.get_stack()},
                              RequestContext(request))


@login_required()
@staff_member_required
def similarities(request, course_short_title=None):
    elaboration = Elaboration.objects.get(pk=request.session.get('elaboration_id', ''))
    challenge_elaborations = Elaboration.objects.filter(challenge=elaboration.challenge,
                                                        submission_time__isnull=False).exclude(pk=elaboration.id)

    similarities = []
    if elaboration.elaboration_text:
        for challenge_elaboration in challenge_elaborations:
            if challenge_elaboration.elaboration_text:
                similarity = {}
                s = SequenceMatcher(lambda x: x == " ",
                                    elaboration.elaboration_text,
                                    challenge_elaboration.elaboration_text)

                if (s.ratio() > 0.5):
                    similarity['elaboration'] = challenge_elaboration
                    similarity['table'] = difflib.HtmlDiff().make_table(elaboration.elaboration_text.splitlines(),
                                                                        challenge_elaboration.elaboration_text.splitlines())
                    similarities.append(similarity)

    return render_to_response('similarities.html', {'similarities': similarities}, RequestContext(request))


@csrf_exempt
@staff_member_required
def save_evaluation(request, course_short_title=None):
    elaboration_id = request.POST['elaboration_id']
    evaluation_text = request.POST['evaluation_text']
    evaluation_points = request.POST['evaluation_points']

    elaboration = Elaboration.objects.get(pk=elaboration_id)
    evaluation = Evaluation.objects.get(submission=elaboration)

    if evaluation_text:
        evaluation.evaluation_text = evaluation_text
    if evaluation_points:
        evaluation.evaluation_points = evaluation_points
    evaluation.save()

    return HttpResponse()


@csrf_exempt
@staff_member_required
def submit_evaluation(request, course_short_title=None):
    elaboration_id = request.POST['elaboration_id']
    evaluation_text = request.POST['evaluation_text']
    evaluation_points = request.POST['evaluation_points']

    elaboration = Elaboration.objects.get(pk=elaboration_id)
    user = RequestContext(request)['user']
    course = elaboration.challenge.course

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
        image_url=elaboration.challenge.image.url,
        link="/challenges/stack?id=" + str(elaboration.challenge.get_stack().id)
    )

    obj.read = False
    obj.save
    return HttpResponse()


@csrf_exempt
@staff_member_required
def reopen_evaluation(request, course_short_title=None):
    elaboration_id = request.POST['elaboration_id']
    elaboration = Elaboration.objects.get(pk=elaboration_id)
    evaluation = Evaluation.objects.get(submission=elaboration)
    course = evaluation.submission.challenge.course

    evaluation.submission_time = None
    evaluation.tutor = RequestContext(request)['user']
    evaluation.save()

    obj, created = Notification.objects.get_or_create(
        user=evaluation.submission.user,
        course=course,
        text=Notification.SUBMISSION_EVALUATED + evaluation.submission.challenge.title,
        image_url=evaluation.submission.challenge.image.url,
        link="/challenges/stack?id=" + str(evaluation.submission.challenge.get_stack().id)
    )
    obj.creation_time = datetime.now()
    obj.read = False
    obj.save()
    return HttpResponse()


@csrf_exempt
@staff_member_required
def set_appraisal(request, course_short_title=None):
    review_id = request.POST['review_id']
    appraisal = request.POST['appraisal']

    review = Review.objects.get(pk=review_id)
    review.appraisal = appraisal
    review.save()
    if review.appraisal == review.NOTHING:
        Notification.bad_review(review)
    else:
        Notification.enough_peer_reviews(review)
    return HttpResponse()


@csrf_exempt
@login_required()
@staff_member_required
def select_challenge(request, course_short_title=None):
    course = Course.get_or_raise_404(short_title=course_short_title)
    selected_challenge = request.POST['selected_challenge'][:(request.POST['selected_challenge'].rindex('(') - 1)]

    elaborations = []
    challenges = Challenge.objects.filter(title=selected_challenge, course=course)
    for challenge in challenges:
        if Elaboration.get_course_sel_challenge_elaborations(challenge):
            for elaboration in Elaboration.get_course_sel_challenge_elaborations(challenge):
                elaborations.append(elaboration)

    html = render_to_response('overview.html', {'elaborations': elaborations, 'search': True, 'course': course}, RequestContext(request))

    # store selected elaborations in session
    request.session['elaborations'] = serializers.serialize('json', elaborations)
    request.session['selection'] = 'search'
    request.session['selected_challenge'] = selected_challenge
    return html


@csrf_exempt
@login_required()
@staff_member_required
def select_user(request, course_short_title=None):
    course = Course.get_or_raise_404(short_title=course_short_title)
    selected_user = request.POST['selected_user'].split()[0]

    elaborations = []
    user = AuroraUser.objects.get(username=selected_user)
    elaborations = user.get_course_elaborations(course)

    points = get_points(request, user)
    html = render_to_response('overview.html',
                              {'elaborations': elaborations, 'search': True, 'stacks': points['stacks'],
                               'courses': points['courses'], 'course': course}, RequestContext(request))

    # store selected elaborations in session
    request.session['elaborations'] = serializers.serialize('json', elaborations)
    request.session['selection'] = 'search'
    return html


@login_required()
@staff_member_required
def autocomplete_challenge(request, course_short_title=None):
    course = Course.get_or_raise_404(short_title=course_short_title)
    term = request.GET.get('term', '')
    challenges = Challenge.objects.all().filter(title__istartswith=term, course=course)
    titles = [challenge.title + ' (' + str(challenge.get_sub_elab_count()) + '/' + str(challenge.get_elab_count()) + ')'
              for challenge in challenges]
    response_data = json.dumps(titles, ensure_ascii=False)
    return HttpResponse(response_data, content_type='application/json; charset=utf-8')


@login_required()
@staff_member_required
def autocomplete_user(request, course_short_title=None):
    term = request.GET.get('term', '')
    studies = AuroraUser.objects.all().filter(
        Q(username__istartswith=term) | Q(first_name__istartswith=term) | Q(last_name__istartswith=term) | Q(
            nickname__istartswith=term))
    names = [(studi.username + ' ' + studi.nickname + ' ' + studi.last_name) for studi in studies]
    response_data = json.dumps(names, ensure_ascii=False)
    return HttpResponse(response_data, content_type='application/json; charset=utf-8')


@login_required()
@staff_member_required
def autocomplete_tag(request, course_short_title=None):
    term = request.GET.get('term', '')
    tags = AuroraUser.tags.all().filter(
        Q(name__istartswith=term)
    )
    names = [tag.name for tag in tags]
    response_data = json.dumps(names, ensure_ascii=False)
    return HttpResponse(response_data, content_type='application/json; charset=utf-8')


@login_required()
@staff_member_required
def load_reviews(request, course_short_title=None):
    course = Course.get_or_raise_404(short_title=course_short_title)
    if not 'elaboration_id' in request.GET:
        return False;

    elaboration = Elaboration.objects.get(pk=request.GET.get('elaboration_id', ''))
    reviews = Review.objects.filter(elaboration=elaboration, submission_time__isnull=False)

    return render_to_response('task.html', {'elaboration': elaboration, 'reviews': reviews, 'stack': 'stack', 'course':course},
                              RequestContext(request))


@csrf_exempt
@login_required()
@staff_member_required
def review_answer(request, course_short_title=None):
    if request.POST:
        course = Course.get_or_raise_404(short_title=course_short_title)

        data = request.body.decode(encoding='UTF-8')
        data = json.loads(data)

        user = RequestContext(request)['user']
        answers = data['answers']

        review = Review.objects.create(elaboration_id=request.session.get('elaboration_id', ''), reviewer_id=user.id)

        review.appraisal = data['appraisal']
        review.submission_time = datetime.now()
        review.save()
        for answer in answers:
            question_id = answer['question_id']
            text = answer['answer']
            review_question = ReviewQuestion.objects.get(pk=question_id)
            ReviewAnswer(review=review, review_question=review_question, text=text).save()
        if review.appraisal == review.NOTHING:
            Notification.bad_review(review)
        else:
            Notification.enough_peer_reviews(review)
        # update overview
        elaborations = Elaboration.get_missing_reviews(course)
        if type(elaborations) == list:
            elaborations.sort(key=lambda elaboration: elaboration.submission_time)
        else:
            elaborations.order_by('submission_time')
        request.session['elaborations'] = serializers.serialize('json', elaborations)
    return HttpResponse()


@login_required()
@staff_member_required
def back(request, course_short_title=None):
    selection = request.session.get('selection', 'error')
    course = Course.get_or_raise_404(short_title=course_short_title)

    if selection == "search":
        return HttpResponse()
    if selection == "missing_reviews":
        elaborations = Elaboration.get_missing_reviews(course)
    if selection == "top_level_challenges":
        elaborations = Elaboration.get_top_level_challenges()
    if selection == "non_adequate_work":
        elaborations = Elaboration.get_non_adequate_work()
    if selection == "complaints":
        elaborations = Elaboration.get_complaints(RequestContext(request))
    if selection == "awesome":
        elaborations = Elaboration.get_awesome()
    if selection == "evaluated_non_adequate_work":
        elaborations = Elaboration.get_evaluated_non_adequate_work()

    # update overview
    if type(elaborations) == list:
        elaborations.sort(key=lambda elaboration: elaboration.submission_time)
    else:
        elaborations.order_by('submission_time')
    request.session['elaborations'] = serializers.serialize('json', elaborations)

    return HttpResponse()


@login_required()
@staff_member_required
def reviewlist(request, course_short_title=None):
    elaboration = Elaboration.objects.get(pk=request.session.get('elaboration_id', ''))
    reviews = Review.objects.filter(reviewer=elaboration.user, submission_time__isnull=False).order_by(
        'elaboration__challenge__id')

    return render_to_response('reviewlist.html', {'reviews': reviews}, RequestContext(request))


@login_required()
@staff_member_required
def search_user(request, course_short_title=None):
    course = Course.get_or_raise_404(short_title=course_short_title)
    if request.GET:
        user = AuroraUser.objects.get(pk=request.GET['id'])
        elaborations = user.get_course_elaborations(course)

        # sort elaborations by submission time
        if type(elaborations) == list:
            elaborations.sort(key=lambda elaboration: elaboration.submission_time)
        else:
            elaborations.order_by('submission_time')

        # store selected elaborations in session
        request.session['elaborations'] = serializers.serialize('json', elaborations)
        request.session['selection'] = 'search'

    return evaluation(request, course_short_title)


@login_required()
@staff_member_required
def sort(request, course_short_title=None):
    course = Course.get_or_raise_404(short_title=course_short_title)

    elaborations = []
    for serialized_elaboration in serializers.deserialize('json', request.session.get('elaborations', {})):
        elaborations.append(serialized_elaboration.object)

    if request.GET.get('data', '') == "date_asc":
        elaborations.sort(key=lambda elaboration: elaboration.submission_time)
    if request.GET.get('data', '') == "date_desc":
        elaborations.sort(key=lambda elaboration: elaboration.submission_time, reverse=True)
    if request.GET.get('data', '') == "elab_asc":
        elaborations.sort(key=lambda elaboration: elaboration.challenge.title)
    if request.GET.get('data', '') == "elab_desc":
        elaborations.sort(key=lambda elaboration: elaboration.challenge.title, reverse=True)

    # store selected elaborations in session
    request.session['elaborations'] = serializers.serialize('json', elaborations)
    request.session['count'] = len(elaborations)

    data = {
        'overview_html': render_to_string('overview.html', {'elaborations': elaborations, 'course': course}, RequestContext(request)),
        'menu_html': render_to_string('menu.html', {
            'count_' + request.session.get('selection', ''): request.session.get('count', '0'),
            'stabilosiert_' + request.session.get('selection', ''): 'stabilosiert', 'course': course,
        }, RequestContext(request)),
        'selection': request.session['selection']
    }

    return HttpResponse(json.dumps(data))


@login_required()
@staff_member_required
def get_points(request, user):
    data = {}
    course_ids = CourseUserRelation.objects.filter(user=user).values_list('course', flat=True)
    courses = Course.objects.filter(id__in=course_ids)
    data['courses'] = courses
    data['stacks'] = []
    for course in courses:
        stack_data = {}
        course_stacks = Stack.objects.all().filter(course=course)
        stack_data['course_title'] = course.title
        stack_data['course_stacks'] = []
        points_sum = 0
        for stack in course_stacks:
            stack_data['course_stacks'].append({
                'stack': stack,
                'points': stack.get_points(user)
            })
            points_sum += stack.get_points(user)
        stack_data['sum'] = points_sum
        data['stacks'].append(stack_data)

    return data

@csrf_exempt
@staff_member_required
def add_tags(request, course_short_title=None):
    text = request.POST['text']
    user_id = request.POST['user_id']

    user = AuroraUser.objects.get(pk=user_id)
    user.add_tags_from_text(text)

    return render_to_response('tags.html', {'user': user}, context_instance=RequestContext(request))

@csrf_exempt
@staff_member_required
def remove_tag(request, course_short_title=None):
    tag = request.POST['tag']
    user_id = request.POST['user_id']

    user = AuroraUser.objects.get(pk=user_id)
    user.remove_tag(tag)

    return render_to_response('tags.html', {'user': user}, context_instance=RequestContext(request))