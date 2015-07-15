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
from Review.models import Review, ReviewEvaluation
from ReviewQuestion.models import ReviewQuestion
from ReviewAnswer.models import ReviewAnswer
from Elaboration.models import Elaboration
from Evaluation.views import get_points
from Challenge.models import Challenge
from Statistics.views import create_stat_data


def course_selection(request):
    if not request.user.is_authenticated():
        if 'sKey' in request.GET:
            from AuroraUser.views import sso_auth_callback
            return sso_auth_callback(request)

    data = {'courses': Course.objects.all()}
    return render_to_response('course_selection.html', data)


def home(request, course_short_title=None):
    if not request.user.is_authenticated():
        return redirect(reverse('User:login', args=(course_short_title, )))

    user = RequestContext(request)['user']
    course = Course.get_or_raise_404(course_short_title)
    data = get_points(request, user, course)
    data = create_stat_data(course,data)
    context = RequestContext(request, {'newsfeed': data['course']})

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

    ReviewID Task_ID AuthorOfReviewedElab_MNr ReviewedElab_ID ReviewAuthor_MNr ReviewPublicFields_∑chars ReviewLVAteamFields_∑chars ReviewEvaluation_value  FullText
        wobei FullText = ReviewFrage1_ID+':'+Answer1_Text+'¶'+ReviewFrage2_ID+':'+Answer2_Text+'¶'+usw.
        und alle CR in <br> und alle TAB in <tab>
    """
    reviews = Review.objects.all().prefetch_related()
    result = ""
    for review in reviews:
        fulltext = ''
        public_chars = 0
        lva_team_chars = 0
        questions = ReviewQuestion.objects.filter(challenge=review.elaboration.challenge)
        review_evaluation = None
        try:
            review_evaluation = ReviewEvaluation.objects.filter(review=review)[0].appraisal
        except:
            # no review evaluation for this review
            pass
        for question in questions:
            answer_text = ''
            try:
                answer_text = ReviewAnswer.objects.filter(review=review, review_question=question)[0].text
            except:
                pass
            if question.visible_to_author:
                public_chars += len(answer_text)
            else:
                lva_team_chars += len(answer_text)
            formatted_text = answer_text.replace('/n', '<br>').replace('/t', '<tab>')
            fulltext += '{}:{}¶'.format(question.id, formatted_text)

        result += "\t".join(["{}"] * 9).format(
            review.id,
            review.elaboration.challenge.id,
            review.elaboration.user.matriculation_number,
            review.elaboration.id,
            review.reviewer.matriculation_number,
            public_chars,
            lva_team_chars,
            review_evaluation,
            fulltext
        )
        result += "\n"
    return result


@login_required()
@staff_member_required
def result_reviews(request):
    result = get_result_reviews()

    return HttpResponse(result, mimetype="text/plain; charset=utf-8")
