from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q, Sum, Count

from Elaboration.models import Elaboration
from Course.models import Course
from Challenge.models import Challenge
from AuroraUser.models import AuroraUser
from Evaluation.models import Evaluation
from Review.models import Review, ReviewEvaluation
from Comments.models import Comment


@staff_member_required
def statistics(request, course_short_title=None):
    data = {}
    course = Course.get_or_raise_404(course_short_title)
    data['course'] = course
    data['students'] = AuroraUser.objects.filter(is_staff=False, is_superuser=False).count()
    data['students_with_at_least_one_submission'] = students_with_at_least_one_submission(course)
    data['started_challenges'] = started_challenges(course)
    data['elaborations'] = elaborations(course)
    data['students_with_more_than_30_points'] = students_with_more_than_x_points(course, 30)
    data['students_with_more_than_35_points'] = students_with_more_than_x_points(course, 35)
    data['students_with_more_than_40_points'] = students_with_more_than_x_points(course, 40)
    data['students_with_more_than_45_points'] = students_with_more_than_x_points(course, 45)
    data['students_with_more_than_50_points'] = students_with_more_than_x_points(course, 50)
    data['students_with_more_than_55_points'] = students_with_more_than_x_points(course, 55)
    data['students_with_more_than_60_points'] = students_with_more_than_x_points(course, 60)
    data['review_evaluations'] = review_evaluations(course)
    data['reviews'] = reviews(course)
    data['commenter_top_25'] = commenter_top_x(course, 25)
    data['tutors'] = tutor_statistics(course)
    return render_to_response('statistics.html', data, context_instance=RequestContext(request))


def students_with_at_least_one_submission(course):
    final_challenge_ids = Challenge.get_final_challenge_ids()
    elaborations = (
        Elaboration.objects
            .filter(challenge__course=course)
            .filter(challenge__id__in=final_challenge_ids)
            .filter(submission_time__isnull=False)
            .values_list('user__id', flat=True)
    )
    elaborations = list(set(elaborations))  # make user ids distinct
    return len(elaborations)


def started_challenges(course):
    elaborations = (
        Elaboration.objects
            .filter(challenge__course=course)
            .exclude(Q(elaboration_text='') & Q(uploadfile__isnull=True))
            .count()
    )
    return elaborations


def elaborations(course):
    return (
        Elaboration.objects
            .filter(challenge__course=course)
            .count()
    )


def students_with_more_than_x_points(course, x):
    users = (
        Evaluation.objects
            .filter(submission__challenge__course=course)
            .filter(submission_time__isnull=False)
            .values('submission__user')
            .annotate(total_points=Sum('evaluation_points'))
            .filter(total_points__gte=x)
            .count()
    )
    return users


def review_evaluations(course):
    return (
        ReviewEvaluation.objects
            .filter(review__elaboration__challenge__course=course)
            .count()
    )


def reviews(course):
    return (
        Review.objects
            .filter(elaboration__challenge__course=course)
            .count()
    )


def commenter_top_x(course, x):
    commenters = (
        Comment.objects
            .values('author', 'author__nickname', 'author__is_staff')
            .annotate(count=Count('author'))
            .order_by('-count')
        [:x]
    )
    return commenters


def tutor_statistics(course):
    tutors = AuroraUser.objects.filter(is_staff=True).values('id', 'nickname').order_by('id')
    for tutor in tutors:
        tutor['evaluations'] = (
            Evaluation.objects
                .filter(submission__challenge__course=course)
                .filter(submission_time__isnull=False)
                .filter(tutor__id=tutor['id'])
                .count()
        )
        tutor['reviews'] = (
            Review.objects
            .filter(elaboration__challenge__course=course)
            .filter(reviewer__id=tutor['id'])
            .count()
        )
        tutor['comments'] = (
            Comment.objects
            .filter(author__id=tutor['id'])
            .count()
        )
    return tutors