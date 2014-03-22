from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^challenges/$', 'Challenge.views.challenges'),
    url(r'^challenges/stack$', 'Challenge.views.stack'),
    url(r'^challenges/challenge$', 'Challenge.views.challenge'),
)