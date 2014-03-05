import json
from datetime import datetime

from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from Review.models import Review
from Elaboration.models import Elaboration
from Challenge.models import Challenge
from ReviewQuestion.models import ReviewQuestion
from ReviewAnswer.models import ReviewAnswer
from Notification.models import Notification

def create_context_review(request):
    data = {}
    if 'id' in request.GET:
        user = RequestContext(request)['user']
        challenge = Challenge.objects.get(pk=request.GET.get('id'))
        if challenge.get_stack().is_blocked(user):
            return None
        review = Review.get_open_review(challenge, user)
        if not review:
            if challenge.has_enough_user_reviews(user):
                return None
            review_candidate = Elaboration.get_review_candidate(challenge, user)
            if review_candidate:
                review = Review(elaboration=review_candidate, reviewer=user)
                review.save()
            else:
                return None
        data['review'] = review
        data['stack_id'] = challenge.get_stack().id
        review_questions = ReviewQuestion.objects.filter(challenge=challenge).order_by("order")
        data['questions'] = review_questions
    return data


@login_required()
def review(request):
    data = create_context_review(request)
    return render_to_response('review.html', data, context_instance=RequestContext(request))


@login_required()
def review_page(request):
    data = create_context_review(request)
    return render_to_response('review_page.html', data, context_instance=RequestContext(request))


@login_required()
def review_answer(request):
    user = RequestContext(request)['user']
    course = RequestContext(request)['last_selected_course']
    if request.POST:
        data = request.body.decode(encoding='UTF-8')
        data = json.loads(data)
        import pprint
        pprint(data)
        review_id = data['review_id']
        answers = data['answers']
        review = Review.objects.get(pk=review_id)
        review.appraisal = data['appraisal']
        for answer in answers:
            question_id = answer['question_id']
            text = answer['answer']
            review_question = ReviewQuestion.objects.get(pk=question_id)
            ReviewAnswer(review=review, review_question=review_question, text=text).save()
            # send notifications
        if review.appraisal == review.FAIL or review.appraisal == review.NOTHING:
            Notification(
                user=review.elaboration.user,
                course=course,
                text=Notification.BAD_REVIEW + review.elaboration.challenge.title,
                image_url=review.elaboration.challenge.image.url,
                link="/challenges/received_challenge_reviews/?id=" + str(review.elaboration.challenge.id)
            ).save()
        else:
            final_challenge = review.elaboration.challenge.get_final_challenge()
            if final_challenge.is_enabled_for_user(review.elaboration.user):
                obj, created = Notification.objects.get_or_create(
                    user=review.elaboration.user,
                    course=course,
                    text=Notification.ENOUGH_PEER_REVIEWS + final_challenge.title,
                    image_url=final_challenge.image.url,
                    link="/challenges/stack?id=" + str(review.elaboration.challenge.get_stack().id)
                )
        review.submission_time = datetime.now()
        review.save()
    return HttpResponse()

def create_context_view_review(request):
    data = {}
    if 'id' in request.GET:
        user = RequestContext(request)['user']
        challenge = Challenge.objects.get(pk=request.GET.get('id'))
        elaboration = Elaboration.objects.filter(challenge=challenge, user=user)[0]
        reviews = Review.objects.filter(elaboration=elaboration).order_by("appraisal")
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


@login_required()
def received_challenge_reviews(request):
    data = create_context_view_review(request)
    return render(request, 'view_review.html', data)


@login_required()
def received_challenge_reviews_page(request):
    data = create_context_view_review(request)
    return render(request, 'view_review_page.html', data)