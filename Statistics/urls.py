from django.conf.urls import patterns, url

import Statistics.views

urlpatterns = patterns('',
                       url(r'^$', Statistics.views.statistics, name='home'),
                       )