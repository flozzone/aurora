from django.conf.urls import patterns, url

import Evaluation.views

urlpatterns = patterns('',
    url(r'^$', Evaluation.views.evaluation, name='home'),
    url(r'^detail$', Evaluation.views.detail, name='detail'),
    url(r'^back/$', Evaluation.views.back, name='back'),
    url(r'^stack/$', Evaluation.views.stack, name='tasks'),
    url(r'^others/$', Evaluation.views.others, name='others'),
    url(r'^challenge_txt/$', Evaluation.views.challenge_txt, name='task_description'),
    url(r'^similarities/$', Evaluation.views.similarities, name='similarities'),
    url(r'^reviewlist/$', Evaluation.views.reviewlist, name='reviews'),
    url(r'^missing_reviews$', Evaluation.views.missing_reviews, name='missing_reviews'),
    url(r'^non_adequate_work$', Evaluation.views.non_adequate_work, name='non_adequate_work'),
    url(r'^top_level_tasks$', Evaluation.views.top_level_tasks, name='top_level_tasks'),
    url(r'^complaints$', Evaluation.views.complaints, name='complaints'),
    url(r'^questions/$', Evaluation.views.questions, name='questions'),
    url(r'^evaluated_non_adequate_work$', Evaluation.views.evaluated_non_adequate_work, name='evaluated_non_adequate_work'),
    url(r'^awesome$', Evaluation.views.awesome, name='awesome'),

    url(r'^autocomplete_challenge/$', Evaluation.views.autocomplete_challenge),
    url(r'^autocomplete_user/$', Evaluation.views.autocomplete_user),
    url(r'^select_challenge/$', Evaluation.views.select_challenge),
    url(r'^select_user/$', Evaluation.views.select_user),
    url(r'^sort$', Evaluation.views.sort),

    url(r'^save_evaluation/$', Evaluation.views.save_evaluation),
    url(r'^submit_evaluation/$', Evaluation.views.submit_evaluation),
    url(r'^reopen_evaluation/$', Evaluation.views.reopen_evaluation),
    url(r'^set_appraisal/$', Evaluation.views.set_appraisal),
    url(r'^search/$', Evaluation.views.search),
    url(r'^load_reviews/$', Evaluation.views.load_reviews),
    url(r'^evaluation/review_answer/$', Evaluation.views.review_answer),
    url(r'^evaluation/user$', Evaluation.views.search_user),
    url(r'^evaluation/elab$', Evaluation.views.search_elab),
    url(r'^start_evaluation$', Evaluation.views.start_evaluation),
)