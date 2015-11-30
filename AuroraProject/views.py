from django.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from datetime import datetime
from django.core.urlresolvers import reverse

from Course.models import Course
from AuroraUser.models import AuroraUser
from Evaluation.models import Evaluation
from Review.models import Review
from ReviewAnswer.models import ReviewAnswer
from Elaboration.models import Elaboration
from Evaluation.views import get_points
from Challenge.models import Challenge
from Statistics.views import create_stat_data
from Faq.models import Faq


def get_next_url(request):
    if 'next' in request.GET:
        return request.GET['next']
    elif 'param' in request.GET:
        return request.GET['param']
    return None


def course_from_next_url(next):
    course = None
    try:
        course = next.split('/')[1]
    except IndexError:
        pass
    finally:
        return course


def course_selection(request):

    # store next_url if available inside the session
    next_url = get_next_url(request)
    if next_url:
        request.session['next_url'] = next_url

    if not request.user.is_authenticated():
        if 'sKey' in request.GET:
            from AuroraUser.views import sso_auth_callback
            return sso_auth_callback(request)

    # automatically redirect the user to its course login page
    # if a next_url is defined.
    if next_url and course_from_next_url(next_url):
        return redirect(reverse("User:login", args=(course_from_next_url(next_url), )))

    data = {'courses': Course.objects.all(), 'next': next}
    return render_to_response('course_selection.html', data)


def home(request, course_short_title=None):
    if not request.user.is_authenticated():
        return redirect(reverse('User:login', args=(course_short_title, )))

    user = RequestContext(request)['user']
    course = Course.get_or_raise_404(course_short_title)
    data = get_points(request, user, course)
    data = create_stat_data(course,data)
    faq_list = Faq.get_faqs(course_short_title)
    context = RequestContext(request, {'newsfeed': data['course'], 'faq_list': faq_list})

    return render_to_response('home.html', data, context)


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
    for user in AuroraUser.objects.filter(is_staff=False):
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
    for evaluation in evals:
        elab = evaluation.submission
        s += "\t".join(["{}"] * 11).format(
            str(elab.user.matriculation_number),
            str(elab.id),
            elab.challenge.title,
            str(elab.challenge.id),
            time_to_unix_string(elab.creation_time),
            time_to_unix_string(elab.submission_time),
            evaluation.id,
            evaluation.tutor.display_name,
            time_to_unix_string(evaluation.creation_date),
            time_to_unix_string(evaluation.submission_time),
            str(evaluation.evaluation_points)
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
