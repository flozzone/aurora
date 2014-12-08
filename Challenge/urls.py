from django.conf.urls import patterns, url

import Challenge.views

urlpatterns = patterns('',
                       url(r'stack$', Challenge.views.stack, name='stack'),
                       url(r'challenge$', Challenge.views.challenge),
                       url(r'$', Challenge.views.challenges, name='home'),
                       )