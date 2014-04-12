from django.conf.urls import patterns, url
from Evaluation import views as evaluation_views
from django.http import HttpResponsePermanentRedirect

urlpatterns = patterns('',
    url(r'^evaluation/$', 'Evaluation.views.evaluation'),
    url(r'^save_evaluation/$', 'Evaluation.views.save_evaluation'),
    url(r'^submit_evaluation/$', 'Evaluation.views.submit_evaluation'),
    url(r'^reopen_evaluation/$', 'Evaluation.views.reopen_evaluation'),
    url(r'^overview/$', 'Evaluation.views.overview'),
    url(r'^questions/$', 'Evaluation.views.questions'),
    url(r'^detail/$', 'Evaluation.views.detail'),
    url(r'^stack/$', 'Evaluation.views.stack'),
    url(r'^others/$', 'Evaluation.views.others'),
    url(r'^challenge_txt/$', 'Evaluation.views.challenge_txt'),
    url(r'^set_appraisal/$', 'Evaluation.views.set_appraisal'),
    url(r'^select_challenge/$', 'Evaluation.views.select_challenge'),
    url(r'^select_user/$', 'Evaluation.views.select_user'),
    url(r'^search/$', 'Evaluation.views.search'),
    url(r'^autocomplete_challenge/$', 'Evaluation.views.autocomplete_challenge'),
    url(r'^autocomplete_user/$', 'Evaluation.views.autocomplete_user'),
    url(r'^load_reviews/$', 'Evaluation.views.load_reviews'),
    url(r'^evaluation/review_answer/$', 'Evaluation.views.review_answer'),
    url(r'^back/$', 'Evaluation.views.back'),
    url(r'^reviewlist/$', 'Evaluation.views.reviewlist'),
    url(r'^evaluation/user$', 'Evaluation.views.search_user'),
    url(r'^evaluation/elab$', 'Evaluation.views.search_elab'),
    url(r'^start_evaluation$', 'Evaluation.views.start_evaluation'),
)