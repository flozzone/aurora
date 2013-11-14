from django.conf.urls import patterns, url
from Evaluation import views as evaluation_views
from django.http import HttpResponsePermanentRedirect

urlpatterns = patterns('',
    url(r'^evaluation/$', 'Evaluation.views.evaluation'),
    #url(r'^challenges/stack$', 'Challenge.views.challenges_stack'),
    #url(r'^challenges/challenge$', 'Challenge.views.challenge_detail'),
    #url(r'^challenges/submit$', 'Challenge.views.submit_challenge'),
    #url(r'^challenges/autosave/$', 'Elaboration.views.save_elaboration'),
    url(r'^autocomplete_challenge/$', 'Evaluation.views.autocomplete_challenge', name='evaluation_autocomplete_challenge'),
    url(r'^autocomplete_stack/$', 'Evaluation.views.autocomplete_stack', name='evaluation_autocomplete_stack'),
    url(r'^autocomplete_user/$', 'Evaluation.views.autocomplete_user', name='evaluation_autocomplete_user'),
    url(r'^search/$', 'Evaluation.views.search', name='evaluation_search'),
    url(r'^submission/$', 'Evaluation.views.get_submission'),
    url(r'^submissions/$', 'Evaluation.views.get_submissions'),
)