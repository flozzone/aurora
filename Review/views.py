from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from PortfolioUser.models import PortfolioUser
from Review.models import Review
from Elaboration.models import Elaboration
from Challenge.models import Challenge
from ReviewQuestion.models import ReviewQuestion

def create_context_review(request):
    data = {}
    if 'id' in request.GET:
        user=PortfolioUser.objects.filter(user_ptr=request.user)[0]
        challenge = Challenge.objects.get(pk=request.GET.get('id'))
        review = Review.getOpenReview(challenge, user)
        if review:
            print("Open Review: " + str(review))
        else:
            print("No open review! assigning a random one")
            review_candidate = Elaboration.getReviewCandidate(challenge, user)
            if review_candidate:
                print(review_candidate.elaboration_text)
                review = Review(elaboration=review_candidate, reviewer=user)
                review.save()
            else:
                print("there should at least be the dummy elaborations")
                return None
        data['review'] = review
        review_questions = ReviewQuestion.objects.filter(challenge=challenge).order_by("order")
        print(review_questions)
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