import os
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from Challenge.models import Challenge
from Course.models import Course
from Elaboration.models import Elaboration
from AuroraUser.models import AuroraUser
from Stack.models import Stack, StackChallengeRelation
from Evaluation.models import Evaluation
from FileUpload.models import UploadFile
from Review.models import Review
from Elaboration.models import Elaboration
from Challenge.models import Challenge
from ReviewQuestion.models import ReviewQuestion
from ReviewAnswer.models import ReviewAnswer
from django.http import Http404

@login_required()
def stack(request, course_short_title=None):
    data = create_context_stack(request, course_short_title)
    return render_to_response('stack.html', data, context_instance=RequestContext(request))


def create_context_stack(request, course_short_title):
    data = {}

    if 'id' not in request.GET:
        return data

    user = RequestContext(request)['user']
    context_stack = Stack.objects.get(pk=request.GET.get('id'))
    data['stack'] = context_stack
    data['stack_blocked'] = context_stack.is_blocked(user)
    stack_challenges = StackChallengeRelation.objects.all().filter(stack=context_stack)
    challenges_active = []
    challenges_inactive = []
    for stack_challenge in stack_challenges:
        if not stack_challenge.challenge.is_enabled_for_user(user):
            challenges_inactive.append(stack_challenge.challenge)
            continue

        reviews = []
        for review in stack_challenge.challenge.get_reviews_written_by_user(user):
            reviews.append({
                'review': review,
                'submitted': review.submission_time is not None
            })
        for i in range(Challenge.reviews_per_challenge - len(reviews)):
            reviews.append({})
        challenge_active = {
            'challenge': stack_challenge.challenge,
            'submitted': stack_challenge.challenge.submitted_by_user(user),
            'reviews': reviews,
            'status': stack_challenge.challenge.get_status_text(user)
        }
        elaboration = Elaboration.objects.filter(challenge=stack_challenge.challenge, user=user)
        if elaboration:
            elaboration = elaboration[0]
            challenge_active['success'] = len(elaboration.get_success_reviews())
            challenge_active['nothing'] = len(elaboration.get_nothing_reviews())
            challenge_active['fail'] = len(elaboration.get_fail_reviews())
            challenge_active['awesome'] = len(elaboration.get_awesome_reviews())
            evaluation = elaboration.get_evaluation()
            if evaluation:
                challenge_active['points'] = evaluation.evaluation_points
        challenges_active.append(challenge_active)
    data['challenges_active'] = challenges_active
    data['challenges_inactive'] = challenges_inactive
    data['course'] = Course.get_or_raise_404(course_short_title)

    return data


@login_required()
def challenges(request, course_short_title=None):
    data = {}

    course = Course.get_or_raise_404(short_title=course_short_title)
    data['course'] = course

    user = RequestContext(request)['user']
    course_stacks = Stack.objects.all().filter(course=course)
    data['course_stacks'] = []
    for stack in course_stacks:
        data['course_stacks'].append({
            'stack': stack,
            'status': stack.get_status_text(user),
            'points': stack.get_points(user)
        })
    return render_to_response('challenges.html', data, context_instance=RequestContext(request))


def create_context_challenge(request, course_short_title):
    data = {}
    course = Course.get_or_raise_404(short_title=course_short_title)
    data['course'] = course

    if 'id' in request.GET:
        try:
            challenge = Challenge.objects.get(pk=request.GET.get('id'))
        except:
            raise Http404
        user = RequestContext(request)['user']
        data['challenge'] = challenge
        data['review_questions'] = []
        for review_question in ReviewQuestion.objects.filter(challenge=challenge, visible_to_author=True).order_by("order"):
            data['review_questions'].append(review_question.text)

        # Create the elaboration to be able to upload files immediately
        Elaboration.objects.get_or_create(challenge=challenge, user=user)

        if Elaboration.objects.filter(challenge=challenge, user=user).exists():
            elaboration = Elaboration.objects.get(challenge=challenge, user=user)
            data['elaboration'] = elaboration
            data['accepted'] = elaboration.is_started()
            data['success'] = elaboration.get_success_reviews()
            data['nothing'] = elaboration.get_nothing_reviews()
            data['fail'] = elaboration.get_fail_reviews()
            if Evaluation.objects.filter(submission=elaboration).exists():
                data['evaluation'] = Evaluation.objects.filter(submission=elaboration)[0]

        if challenge.is_final_challenge():
            if challenge.is_in_lock_period(RequestContext(request)['user'], course):
                data['lock'] = challenge.is_in_lock_period(RequestContext(request)['user'], course)
    return data


@login_required()
def challenge(request, course_short_title=None):
    data = create_context_challenge(request, course_short_title)
    user = RequestContext(request)['user']
    if not data['challenge'].is_enabled_for_user(user) and not user.is_staff:
        return render_to_response('challenge_inactive.html', data, context_instance=RequestContext(request))
    if 'elaboration' in data:
        data = create_context_view_review(request, data)

    return render_to_response('challenge.html', data, context_instance=RequestContext(request))


def create_context_view_review(request, data):
    if 'id' in request.GET:
        user = RequestContext(request)['user']
        challenge = Challenge.objects.get(pk=request.GET.get('id'))
        elaboration = Elaboration.objects.filter(challenge=challenge, user=user)[0]
        reviews = Review.objects.filter(elaboration=elaboration, submission_time__isnull=False).order_by("appraisal")
        data['reviews'] = []
        for review in reviews:
            review_data = {}
            review_data['review_id'] = review.id
            review_data['review'] = review
            review_data['appraisal'] = review.get_appraisal_display()
            review_data['questions'] = []
            for review_question in ReviewQuestion.objects.filter(challenge=challenge).order_by("order"):
                question_data = {}
                review_answer = ReviewAnswer.objects.filter(review=review, review_question=review_question)[0]
                question_data['question'] = review_question.text
                question_data['answer'] = review_answer.text
                review_data['questions'].append(question_data)
            data['reviews'].append(review_data)
    return data
