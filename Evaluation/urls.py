from django.conf.urls import patterns, url
from Evaluation import views as evaluation_views
from django.http import HttpResponsePermanentRedirect

urlpatterns = patterns('',
    url(r'^evaluation/$', 'Evaluation.views.evaluation'),
    url(r'^submit_evaluation/$', 'Evaluation.views.submit_evaluation'),
    url(r'^overview/$', 'Evaluation.views.overview'),
    url(r'^update_overview/$', 'Evaluation.views.update_overview'),
    url(r'^detail/$', 'Evaluation.views.detail'),
    url(r'^stack/$', 'Evaluation.views.stack'),
    url(r'^others/$', 'Evaluation.views.others'),
    url(r'^challenge_txt/$', 'Evaluation.views.challenge_txt'),
)