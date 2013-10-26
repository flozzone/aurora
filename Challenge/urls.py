from django.conf.urls import patterns, url
from Challenge import views as challenge_views
from django.http import HttpResponsePermanentRedirect

urlpatterns = patterns('',
    url(r'^challenges/$', 'Challenge.views.challenges_open'),
    url(r'^challenges/challenge$', 'Challenge.views.challenge_detail'),
)