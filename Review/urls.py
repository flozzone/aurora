from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^$', 'Review.views.review'),
    url(r'^review_answer/$', 'Review.views.review_answer'),
)