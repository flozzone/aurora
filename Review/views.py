from django.shortcuts import render_to_response
from django.template import RequestContext

import json
from django.contrib.auth.decorators import login_required
from PortfolioUser.models import PortfolioUser
from Review.models import Review
from Elaboration.models import Elaboration
from Challenge.models import Challenge
from ReviewQuestion.models import ReviewQuestion
from ReviewAnswer.models import ReviewAnswer
from django.http import HttpResponse
from datetime import datetime

def create_context_review(request):
    data = {}
    if 'id' in request.GET:
        user = PortfolioUser.objects.filter(user_ptr=request.user)[0]
        challenge = Challenge.objects.get(pk=request.GET.get('id'))
        review = Review.get_open_review(challenge, user)
        if not review:
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
    if request.POST:
        data = request.body.decode(encoding='UTF-8')
        data = json.loads(data)
        review_id = data['review_id']
        answers = data['answers']
        for answer in answers:
            question_id = answer['question_id']
            text = answer['answer']
            review_question = ReviewQuestion.objects.get(pk=question_id)
            ReviewAnswer(review_question=review_question, text=text).save()
        review = Review.objects.get(pk=review_id)
        review.appraisal = data['appraisal']
        review.awesome = data['awesome']
        review.submission_time = datetime.now()
        review.save()
    return HttpResponse()
