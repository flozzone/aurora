from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^$', 'slides.views.start'),
    url(r'^livecast/(?P<lecture_id_relative>\d+)/$', 'slides.views.livecast', name="livecast"),
    url(r'^livecast/(?P<lecture_id_relative>\d+)/update_slide/(?P<slide_id>\d+)/(?P<client_timestamp>\d+)/json/$', 'slides.views.livecast_update_slide', name="livecast_update_slide"),
    url(r'^studio/lecture/(?P<lecture_id_relative>\d+)/$', 'slides.views.studio_lecture', name="studio_lecture"),
    url(r'^studio/confusing/$', 'slides.views.studio_marker', {'marker': 'confusing'}, name="studio_confusing"),
    url(r'^studio/important/$', 'slides.views.studio_marker', {'marker': 'important'}, name="studio_important"),
    url(r'^studio/liked/$', 'slides.views.studio_marker', {'marker': 'liked'}, name="studio_liked"),
    url(r'^studio/search/$', 'slides.views.studio_search', name="studio_search"),
    url(r'^mark_slide/(?P<slide_id>\d+)/(?P<marker>(liked|important|confusing))/(?P<value>(true|false|xxx))/json/$', 
        'slides.views.mark_slide', name='mark_slide'),
)