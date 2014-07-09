from django.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import redirect
from django.http import HttpResponse
from email import charset

from Comments.models import CommentReferenceObject
from Stack.models import Stack
from Course.models import Course, CourseUserRelation
from PortfolioUser.models import  PortfolioUser
from Evaluation.models import Evaluation
from Review.models import Review
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


def result_users(request):
    s = ""
    for user in PortfolioUser.objects.filter(is_staff=False):
        s += "\t".join(["{}"] * 7).format(user.matriculation_number,
                                         user.nickname,
                                         user.first_name,
                                         user.last_name,
                                         user.study_code,
                                         str(user.last_activity),
                                         user.statement)
        s += "\n"

    return HttpResponse(s, mimetype="text/plain; charset=utf-8")


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
            elab.user.username + " (" + str(elab.user.matriculation_number) + ")",
            str(elab.id),
            elab.challenge.title,
            str(elab.challenge.id),
            str(elab.creation_time),
            str(elab.submission_time)
        )

        for review in Review.objects.filter(elaboration=elab):
            s += "\t" + str(review.id)
            s += "\t" + str(review.appraisal)
            s += "\t" + str(review.creation_time)
            s += "\t" + str(review.submission_time)

        s += "\n"

    return HttpResponse(s, mimetype="text/plain; charset=utf-8")


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
            elab.user.username + " (" + str(elab.user.matriculation_number) + ")",
            str(elab.id),
            elab.challenge.title,
            str(elab.challenge.id),
            str(elab.creation_time),
            str(elab.submission_time),
            eval.id,
            eval.tutor.display_name,
            str(eval.creation_date),
            str(eval.submission_time),
            str(eval.evaluation_points)
        )

        s += "\n"

    return HttpResponse(s, mimetype="text/plain; charset=utf-8")
