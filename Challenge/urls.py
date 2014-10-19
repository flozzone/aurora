from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'$', 'Challenge.views.challenges', name='home'),
    url(r'/stack$', 'Challenge.views.stack'),
    url(r'/challenge$', 'Challenge.views.challenge'),
)