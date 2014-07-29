from django.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from datetime import datetime

from Comments.models import CommentReferenceObject
from Stack.models import Stack
from Course.models import Course, CourseUserRelation
from PortfolioUser.models import  PortfolioUser
from Evaluation.models import Evaluation
from Review.models import Review
from ReviewAnswer.models import ReviewAnswer
from Elaboration.models import Elaboration
from Challenge.models import Challenge


def home(request):
    if request.user.is_authenticated():
        data = {}
        user = RequestContext(request)['user']

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

        try:
            o = CommentReferenceObject.objects.get(name='newsfeed')
        except CommentReferenceObject.DoesNotExist:
            o = CommentReferenceObject(name='newsfeed')
            o.save()

        context = RequestContext(request, {'newsfeed': o})

        return render_to_response('home.html', data, context)
    elif 'sKey' in request.GET:
        from PortfolioUser.views import sso_auth_callback

        return sso_auth_callback(request)
    else:
        return redirect('/login')

def time_to_unix_string(time):
    if time is None:
        return str(None)

    delta = time - datetime(1970, 1, 1)
    hours = delta.days * 24
    seconds = hours * 3600
    seconds += delta.seconds
    return str(seconds)

@login_required()
@staff_member_required
def result_users(request):
    s = ""
    for user in PortfolioUser.objects.filter(is_staff=False):
        s += "\t".join(["{}"] * 7).format(user.matriculation_number,
                                         user.nickname,
                                         user.first_name,
                                         user.last_name,
                                         user.study_code,
                                         time_to_unix_string(user.last_activity),
                                         user.statement)
        s += "\n"

    return HttpResponse(s, mimetype="text/plain; charset=utf-8")


@login_required()
@staff_member_required
def result_elabs_nonfinal(request):
    """
    username (mnr) TAB elabID TAB challenge-title TAB challenge-ID TAB creation time TAB submission time TAB
    reviewID 1 TAB review-verdict 1 TAB review-creation-date 1 TAB review-submission-date 1 TAB reviewID 2 TAB
    review-verdict 2 TAB review-creation-date 2 TAB review-submission-date 2 TAB usw.
    """

    final_challenge_ids = Challenge.get_final_challenge_ids()
    elabs = Elaboration.objects.exclude(challenge__id__in=final_challenge_ids).prefetch_related()

    s = ""
    for elab in elabs:
        s += "\t".join(["{}"] * 6).format(
            str(elab.user.matriculation_number),
            str(elab.id),
            elab.challenge.title,
            str(elab.challenge.id),
            time_to_unix_string(elab.creation_time),
            time_to_unix_string(elab.submission_time)
        )

        for review in Review.objects.filter(elaboration=elab):
            s += "\t" + str(review.id)
            s += "\t" + str(review.appraisal)
            s += "\t" + time_to_unix_string(review.creation_time)
            s += "\t" + time_to_unix_string(review.submission_time)

        s += "\n"

    return HttpResponse(s, mimetype="text/plain; charset=utf-8")


@login_required()
@staff_member_required
def result_elabs_final(request):
    """
    username(mnr) TAB elabID TAB challenge-title TAB challenge-ID TAB creation time TAB submission time TAB
    evaluationID TAB tutor TAB evaluation-creationdate TAB evaluation-submissiontime TAB evaluation-points
    """

    evals = Evaluation.objects.all().prefetch_related()

    s = ""
    for eval in evals:
        elab = eval.submission
        s += "\t".join(["{}"] * 11).format(
            str(elab.user.matriculation_number),
            str(elab.id),
            elab.challenge.title,
            str(elab.challenge.id),
            time_to_unix_string(elab.creation_time),
            time_to_unix_string(elab.submission_time),
            eval.id,
            eval.tutor.display_name,
            time_to_unix_string(eval.creation_date),
            time_to_unix_string(eval.submission_time),
            str(eval.evaluation_points)
        )

        s += "\n"

    return HttpResponse(s, mimetype="text/plain; charset=utf-8")


def get_result_reviews():
    """
    Since this is so slow (and can be too slow for a application server response, this is also being used
    as a command in Review.

    review-autor (MNr) TAB
    reviewed-elab-autor (MNr) TAB
    reviewed-elab-challenge-ID TAB
    review-creation-date TAB
    review-submission-date TAB
    länge des reviews (number of chars of all fields summiert)
    """
    reviews = Review.objects.all().prefetch_related()
    result = ""
    for review in reviews:
        answers = ReviewAnswer.objects.filter(review=review.id)
        answer_string = ""
        for answer in answers:
            answer_string += answer.text
        length = len(answer_string)

        result += "\t".join(["{}"] * 6).format(
            review.reviewer.username,
            review.elaboration.user.username,
            review.elaboration.challenge_id,
            time_to_unix_string(review.creation_time),
            time_to_unix_string(review.submission_time),
            str(length)
        )

        result += "\n"

    return result

@login_required()
@staff_member_required
def result_reviews(request):
    result = get_result_reviews()

    return HttpResponse(result, mimetype="text/plain; charset=utf-8")
