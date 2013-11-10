from django.conf.urls import patterns, url
from Evaluation import views as evaluation_views
from django.http import HttpResponsePermanentRedirect

urlpatterns = patterns('',
    url(r'^evaluation/$', 'Evaluation.views.evaluation'),
    #url(r'^challenges/stack$', 'Challenge.views.challenges_stack'),
    #url(r'^challenges/challenge$', 'Challenge.views.challenge_detail'),
    #url(r'^challenges/submit$', 'Challenge.views.submit_challenge'),
    #url(r'^challenges/autosave/$', 'Elaboration.views.save_elaboration'),
    url(r'^autocomplete/$', 'Evaluation.views.autocomplete', name='evaluation_autocomplete'),
    url(r'^search/$', 'Evaluation.views.search', name='evaluation_search'),
)