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
    data = create_stat_data(course,data)
    return render_to_response('statistics.html', data, context_instance=RequestContext(request))

def create_stat_data(course, data):
    data['course'] = course
    data['students'] = AuroraUser.objects.filter(is_staff=False, is_superuser=False).count()
    data['students_with_at_least_one_submission'] = students_with_at_least_one_submission(course)
    data['started_challenges'] = started_challenges(course)
    data['elaborations'] = elaborations(course)
    data['students_with_more_than_10_points'] = students_with_x_or_more_points(course, 10)
    data['students_with_more_than_20_points'] = students_with_x_or_more_points(course, 20)
    data['students_with_more_than_30_points'] = students_with_x_or_more_points(course, 30)
    data['students_with_more_than_40_points'] = students_with_x_or_more_points(course, 40)
    data['students_with_more_than_47_points'] = students_with_x_or_more_points(course, 47)
    data['students_with_more_than_53_points'] = students_with_x_or_more_points(course, 53)
    data['students_with_more_than_60_points'] = students_with_x_or_more_points(course, 60)
    data['review_evaluations'] = review_evaluations(course)
    data['review_evaluations_positive'] = review_evaluations_positive(course)
    data['review_evaluations_default'] = review_evaluations_default(course)
    data['review_evaluations_negative'] = review_evaluations_negative(course)
    data['review_evaluations_positive_ratio'] = data['review_evaluations_positive']/data['review_evaluations']*100
    data['review_evaluations_default_ratio'] = data['review_evaluations_default']/data['review_evaluations']*100
    data['review_evaluations_negative_ratio'] = data['review_evaluations_negative']/data['review_evaluations']*100
    data['reviews'] = reviews(course)
    data['commenter_top_25'] = commenter_top_x(course, 25)
    data['tutors'] = tutor_statistics(course)
    data['review_evaluating_students_top_10'] = review_evaluating_students_top_x(course, 10)
    data['evaluated_final_tasks'] = evaluated_final_tasks(course)
    data['not_evaluated_final_tasks'] = not_evaluated_final_tasks(course)
    data['final_tasks'] = final_tasks(course)
    return data

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


def students_with_x_or_more_points(course, x):
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
    review_evaluations = ( ReviewEvaluation.objects
        .filter(review__elaboration__challenge__course=course)
        .count()
    )
    review_evaluations += 1 if review_evaluations == 0 else 0
    return review_evaluations

def review_evaluations_positive(course):
    return (
        ReviewEvaluation.objects
            .filter(review__elaboration__challenge__course=course)
            .filter(appraisal=ReviewEvaluation.POSITIVE)
            .count()
    )


def review_evaluations_default(course):
    return (
        ReviewEvaluation.objects
            .filter(review__elaboration__challenge__course=course)
            .filter(appraisal=ReviewEvaluation.DEFAULT)
            .count()
    )


def review_evaluations_negative(course):
    return (
        ReviewEvaluation.objects
            .filter(review__elaboration__challenge__course=course)
            .filter(appraisal=ReviewEvaluation.NEGATIVE)
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
            .values('author', 'author__nickname', 'author__id', 'author__is_staff')
            .annotate(count=Count('author'))
            .order_by('-count')
        [:x]
    )
    return commenters


def tutor_statistics(course):
    tutors = AuroraUser.objects.filter(is_staff=True).values('id', 'nickname', 'first_name', 'last_name').order_by('id')
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


def review_evaluating_students_top_x(course, x):
    students = (
        ReviewEvaluation.objects
            .filter(review__elaboration__challenge__course=course)
            .values('user__id', 'user__nickname')
            .annotate(count=Count('user'))
            .order_by('-count')
        [:x]
    )
    result = []
    for student in students:
        data = {
            'id': student['user__id'],
            'nickname': student['user__nickname'],
            'count': student['count']
        }

        total = (
            Review.objects
                .filter(elaboration__challenge__course=course)
                .filter(elaboration__user__id=student['user__id'])
                .count()
        )
        data['percent'] = int((data['count'] / total) * 100)
        result.append(data)
    return result


def evaluated_final_tasks(course):
    return (
        Evaluation.objects
            .filter(submission__challenge__course=course)
            .filter(submission_time__isnull=False)
            .count()
    )


def not_evaluated_final_tasks(course):
    return Elaboration.get_top_level_tasks(course).count()


def final_tasks(course):
    final_task_ids = Challenge.get_course_final_challenge_ids(course)

    result = []
    for id in final_task_ids:
        data = {}
        data['id'] = id
        data['title'] = (
            Challenge.objects.get(pk=id).title
        )
        data['evaluated'] = (
            Evaluation.objects
                .filter(submission__challenge__course=course)
                .filter(submission_time__isnull=False)
                .filter(submission__challenge__id=id)
                .count()
        )
        data['not_evaluated'] = (
            Elaboration.get_top_level_tasks(course)
                .filter(challenge__id=id)
                .count()
        )
        result.append(data)
    return result
