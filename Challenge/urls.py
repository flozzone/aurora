from django.conf.urls import patterns, url


urlpatterns = patterns('',
    url(r'^challenges/$', 'Challenge.views.challenges_page'),
    url(r'^challenges/stack$', 'Challenge.views.stack_page'),
    url(r'^challenges/get_stack$', 'Challenge.views.stack'),
    url(r'^challenges/get_challenge$', 'Challenge.views.challenge'),
    url(r'^challenges/challenge$', 'Challenge.views.challenge_page'),
)