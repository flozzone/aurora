import os
from django import template
from Review.models import Review
from ReviewAnswer.models import ReviewAnswer

register = template.Library()

@register.inclusion_tag('review_answers.html')
def render_review_answers(review_id):
    review = Review.objects.get(id=review_id)
    review_answers = ReviewAnswer.objects.filter(review=review).order_by("review_question.order")
    return {'review_answers' : review_answers}