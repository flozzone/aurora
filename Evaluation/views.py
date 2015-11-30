from datetime import datetime
from difflib import SequenceMatcher
import difflib
import json
from django.contrib.contenttypes.models import ContentType
from django.core import serializers
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from taggit.models import TaggedItem
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden

from Challenge.models import Challenge
from Course.models import Course, CourseUserRelation
from Elaboration.models import Elaboration
from Evaluation.models import Evaluation
from AuroraUser.models import AuroraUser
from Review.models import Review, ReviewEvaluation
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
            display_points = request.session.get('display_points', 'error')
            if display_points == "true":
                user = AuroraUser.objects.get(username=request.session.get('selected_user'))
                points = get_points(request, user, course)
                data = {
                    'elaborations': elaborations,
                    'search': True,
                    'stacks': points['stacks'],
                    'courses': points['courses'],
                    'review_evaluation_data': points['review_evaluation_data'],
                    'course': course
                }
            else:
                data = {'elaborations': elaborations, 'search': True, 'course': course}
        elif selection == 'complaints':
            data = {'elaborations': elaborations, 'course': course, 'complaints': 'true'}
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
                               'overview': overview,
                               'count_' + request.session.get('selection', ''): count,
                               'stabilosiert_' + request.session.get('selection', ''): 'stabilosiert',
                               'course': course,
                               'selected_challenge': request.session.get('selected_challenge'),
                               'selected_user': request.session.get('selected_user'),
                               'selected_task': request.session.get('selected_task'),
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
        elaborations = elaborations.order_by('submission_time')

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
        elaborations = elaborations.order_by('submission_time')

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
    elaborations = Elaboration.get_top_level_tasks(course)

    # sort elaborations by submission time
    if type(elaborations) == list:
        elaborations.sort(key=lambda elaboration: elaboration.submission_time)
    else:
        elaborations = elaborations.order_by('submission_time')

    # store selected elaborations in session
    request.session['elaborations'] = serializers.serialize('json', elaborations)
    request.session['selection'] = 'top_level_tasks'
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
    elaborations = list(Elaboration.get_complaints(course))

    # sort elaborations by last comment time
    elaborations.sort(key=lambda elaboration: elaboration.get_last_post_date())

    # store selected elaborations in session
    request.session['elaborations'] = serializers.serialize('json', elaborations)
    request.session['selection'] = 'complaints'
    request.session['count'] = len(elaborations)

    return render_to_response('evaluation.html',
                              {'overview': render_to_string('overview.html', {'elaborations': elaborations, 'course': course, 'complaints': 'true'},
                                                            RequestContext(request)),
                               'count_complaints': request.session.get('count', '0'),
                               'stabilosiert_complaints': 'stabilosiert',
                               'selection': request.session['selection'],
                               'course': course
                              },
                              context_instance=RequestContext(request))


@login_required()
@staff_member_required
def awesome(request, course_short_title=None):
    course = Course.get_or_raise_404(short_title=course_short_title)
    selected_challenge = request.session.get('selected_challenge', 'task...')
    if selected_challenge != 'task...':
        selected_challenge = selected_challenge[:(selected_challenge.rindex('(') - 1)]
        challenge = Challenge.objects.get(title=selected_challenge, course=course)
        elaborations = Elaboration.get_awesome_challenge(course, challenge)
    else:
        elaborations = Elaboration.get_awesome(course)

    # sort elaborations by submission time
    if type(elaborations) == list:
        elaborations.sort(key=lambda elaboration: elaboration.submission_time)
    else:
        elaborations = elaborations.order_by('submission_time')

    # store selected elaborations in session
    request.session['elaborations'] = serializers.serialize('json', elaborations)
    request.session['selection'] = 'awesome'
    request.session['selected_challenge'] = 'task...'
    request.session['count'] = len(elaborations)

    return render_to_response('evaluation.html',
                              {'overview': render_to_string('overview.html', {'elaborations': elaborations, 'course': course},
                                                            RequestContext(request)),
                               'count_awesome': request.session.get('count', '0'),
                               'selected_task': selected_challenge,
                               'stabilosiert_awesome': 'stabilosiert',
                               'selection': request.session['selection'],
                               'course': course
                              },
                              context_instance=RequestContext(request))


@login_required()
@staff_member_required
def questions(request, course_short_title=None):
    course = Course.get_or_raise_404(short_title=course_short_title)
    challenges = Challenge.get_questions(course)

    # store selected challenges in session
    request.session['challenges'] = serializers.serialize('json', challenges)

    # store selected elaborations in session
    elaborations = []
    request.session['elaborations'] = elaborations
    request.session['selection'] = 'questions'
    request.session['count'] = len(challenges)

    return render_to_response('evaluation.html',
                              {'challenges': challenges,
                               'overview': render_to_string('questions.html', {'challenges': challenges, 'course': course},
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
    if selection == "top_level_tasks":
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
        if elaboration.challenge.is_final_challenge():
            params = {'evaluation': evaluation, 'lock': lock, 'selection': 'top-level tasks'}
        else:
            if elaboration.is_reviewed_2times():
                params = {'evaluation': evaluation, 'lock': lock}
            else:
                questions = ReviewQuestion.objects.filter(challenge=elaboration.challenge).order_by("order")
                params = {'questions': questions, 'selection': 'missing reviews'}

    reviews = Review.objects.filter(elaboration=elaboration, submission_time__isnull=False)

    next = prev = None
    index = elaborations.index(elaboration)
    if index + 1 < len(elaborations):
        next = elaborations[index + 1].id
    if not index == 0:
        prev = elaborations[index - 1].id
    count_next = len(elaborations) - index - 1
    count_prev = index

    stack_elaborations = elaboration.user.get_stack_elaborations(elaboration.challenge.get_stack())
    # sort stack_elaborations by submission time
    if type(stack_elaborations) == list:
        stack_elaborations.sort(key=lambda stack_elaboration: stack_elaboration.submission_time)
    else:
        stack_elaborations = stack_elaborations.order_by('submission_time')

    params['elaboration'] = elaboration
    params['stack_elaborations'] = stack_elaborations
    params['reviews'] = reviews
    params['next'] = next
    params['prev'] = prev
    params['count_next'] = count_next
    params['count_prev'] = count_prev
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
        link=reverse('Challenge:stack', args=[course_short_title]) + '?id=' + str(elaboration.challenge.get_stack().id)
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
        link=reverse('Challenge:stack', args=[course_short_title]) + '?id=' + str(evaluation.submission.challenge.get_stack().id)
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
def search(request, course_short_title=None):
    course = Course.get_or_raise_404(short_title=course_short_title)

    selected_challenge = request.POST['selected_challenge']
    selected_user = request.POST['selected_user'].split()[0]
    selected_tag = request.POST['selected_tag']

    challenges = []
    if(selected_challenge != 'task...'):
        challenges = Challenge.objects.filter(title=selected_challenge[:(request.POST['selected_challenge'].rindex('(') - 1)], course=course)
    else:
        challenges = Challenge.objects.filter(course=course)

    user = []
    if(selected_user != 'user...'):
        user = AuroraUser.objects.filter(username=selected_user)
        request.session['display_points'] = "true"
    else:
        user = AuroraUser.objects.all()
        request.session['display_points'] = "false"

    if(selected_tag != 'tag...'):
        aurorauser_ct = ContentType.objects.get_for_model(AuroraUser)
        tagged_items = TaggedItem.objects.filter(content_type=aurorauser_ct, tag__name=selected_tag)
        tagged_user_ids = []
        for ti in tagged_items:
            if not tagged_user_ids.__contains__(ti.content_object):
                tagged_user_ids.append(ti.content_object.id)

        tagged_user = AuroraUser.objects.filter(id__in=tagged_user_ids)
        user = user & tagged_user

    elaborations = []
    if Elaboration.search(challenges, user):
        elaborations = list(Elaboration.search(challenges, user))

    # store selected elaborations in session
    request.session['elaborations'] = serializers.serialize('json', elaborations)
    request.session['selection'] = 'search'
    request.session['selected_challenge'] = selected_challenge
    request.session['selected_user'] = selected_user
    request.session['selected_tag'] = selected_tag

    return evaluation(request, course_short_title)


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
    names = [(studi.username + ' ' + studi.nickname + ' ' + studi.first_name + ' ' + studi.last_name) for studi in studies]
    response_data = json.dumps(names, ensure_ascii=False)
    return HttpResponse(response_data, content_type='application/json; charset=utf-8')


@login_required()
@staff_member_required
def autocomplete_tag(request, course_short_title=None):
    term = request.GET.get('term', '')
    content_type_id = request.GET['content_type_id']

    content_type = ContentType.objects.get_for_id(content_type_id)
    taggable_model = content_type.model_class()
    tags = taggable_model.tags.all().filter(
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


@require_POST
@csrf_exempt
@login_required()
@staff_member_required
def review_answer(request, course_short_title=None):
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
        elaborations = elaborations.order_by('submission_time')
    request.session['elaborations'] = serializers.serialize('json', elaborations)

    if review.elaboration.is_reviewed_2times():
        evaluation_url = reverse('Evaluation:home', args=[course_short_title])
    else:
        evaluation_url = reverse('Evaluation:detail', args=[course_short_title])\
            + "?elaboration_id=" + str(review.elaboration.id)

    return HttpResponse(evaluation_url)


@login_required()
@staff_member_required
def back(request, course_short_title=None):
    selection = request.session.get('selection', 'error')
    course = Course.get_or_raise_404(short_title=course_short_title)

    if selection == "search":
        return HttpResponse()
    if selection == "missing_reviews":
        elaborations = Elaboration.get_missing_reviews(course)
    if selection == "top_level_tasks":
        elaborations = Elaboration.get_top_level_tasks(course)
    if selection == "non_adequate_work":
        elaborations = Elaboration.get_non_adequate_work(course)
    if selection == "complaints":
        elaborations = Elaboration.get_complaints(course)
    if selection == "awesome":
        elaborations = Elaboration.get_awesome(course)
    if selection == "evaluated_non_adequate_work":
        elaborations = Elaboration.get_evaluated_non_adequate_work(course)

    # update overview
    if type(elaborations) == list:
        elaborations.sort(key=lambda elaboration: elaboration.submission_time)
    else:
        elaborations = elaborations.order_by('submission_time')
    request.session['elaborations'] = serializers.serialize('json', elaborations)

    return evaluation(request, course_short_title)


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
            elaborations = elaborations.order_by('submission_time')

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
    if request.GET.get('data', '') == "post_asc":
        elaborations.sort(key=lambda elaboration: elaboration.get_last_post_date())
    if request.GET.get('data', '') == "post_desc":
        elaborations.sort(key=lambda elaboration: elaboration.get_last_post_date(), reverse=True)

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
def get_points(request, user, course):
    is_correct_user_request = RequestContext(request)['user'].id == user.id
    is_staff_request = RequestContext(request)['user'].is_staff
    if not (is_correct_user_request or is_staff_request):
        return HttpResponseForbidden()
    data = {}
    data['course'] = course
    course_ids = CourseUserRelation.objects.filter(user=user).values_list('course', flat=True)
    courses = Course.objects.filter(id__in=course_ids)
    data['courses'] = courses
    data['review_evaluation_data'] = {}
    data['review_evaluation_data']['default_review_evaluations'] = ReviewEvaluation.get_default_review_evaluations(user, course)
    data['review_evaluation_data']['positive_review_evaluations'] = ReviewEvaluation.get_positive_review_evaluations(user, course)
    data['review_evaluation_data']['negative_review_evaluations'] = ReviewEvaluation.get_negative_review_evaluations(user, course)
    data['review_evaluation_data']['review_evaluation_percent'] = ReviewEvaluation.get_review_evaluation_percent(user, course)

    data['stacks'] = []
    for course in courses:
        stack_data = {}
        course_stacks = Stack.objects.all().filter(course=course)
        stack_data['course_title'] = course.title
        stack_data['course_stacks'] = []
        evaluated_points_earned_total = 0
        evaluated_points_available_total = 0
        submitted_points_available_total = 0
        started_points_available_total = 0
        for stack in course_stacks:
            is_submitted = stack.get_final_challenge().submitted_by_user(user)
            is_evaluated = stack.is_evaluated(user)
            is_started = stack.get_first_challenge().is_started(user)
            is_blocked = stack.is_blocked(user)
            points_available = stack.get_points_available()
            points_earned = stack.get_points_earned(user)
            stack_data['course_stacks'].append({
                'stack': stack,
                'is_started': is_started,
                'is_submitted': is_submitted,
                'is_evaluated': is_evaluated,
                'is_blocked': is_blocked,
                'points_earned': points_earned,
                'points_available': points_available,
                'status': stack.get_status_text(user),
            })
            if is_evaluated:
                # skip adding available points to totals for evaluations with 0 points
                if points_earned == 0:
                    continue
                evaluated_points_earned_total += points_earned
                evaluated_points_available_total += points_available
                continue
            if is_submitted:
                submitted_points_available_total += points_available
                continue
            if is_started and not is_blocked:
                started_points_available_total += points_available

        stack_data['evaluated_points_earned_total'] = evaluated_points_earned_total
        stack_data['evaluated_points_available_total'] = evaluated_points_available_total
        stack_data['submitted_points_available_total'] = submitted_points_available_total
        stack_data['started_points_available_total'] = started_points_available_total
        stack_data['lock_period'] = stack.get_final_challenge().is_in_lock_period(user, course)
        data['stacks'].append(stack_data)

    return data

@csrf_exempt
@staff_member_required
def add_tags(request, course_short_title=None):
    text = request.POST['text']
    object_id = request.POST['object_id']
    content_type_id = request.POST['content_type_id']

    content_type = ContentType.objects.get_for_id(content_type_id)
    taggable_object = content_type.get_object_for_this_type(pk=object_id)
    taggable_object.add_tags_from_text(text)

    return render_to_response('tags.html', {'tagged_object': taggable_object}, context_instance=RequestContext(request))

@csrf_exempt
@staff_member_required
def remove_tag(request, course_short_title=None):
    tag = request.POST['tag']
    object_id = request.POST['object_id']
    content_type_id = request.POST['content_type_id']

    content_type = ContentType.objects.get_for_id(content_type_id)
    taggable_object = content_type.get_object_for_this_type(pk=object_id)
    taggable_object.remove_tag(tag)

    return render_to_response('tags.html', {'tagged_object': taggable_object}, context_instance=RequestContext(request))
