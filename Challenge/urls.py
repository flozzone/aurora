from django.conf.urls import patterns, url
from Challenge import views as challenge_views
from django.http import HttpResponsePermanentRedirect

urlpatterns = patterns('',
    url(r'^challenges/$', 'Challenge.views.challenges_page'),
    url(r'^challenges/stack$', 'Challenge.views.stack_page'),
    url(r'^challenges/get_stack$', 'Challenge.views.stack'),
    url(r'^challenges/get_challenge$', 'Challenge.views.challenge'),
    url(r'^challenges/challenge$', 'Challenge.views.challenge_page'),
)