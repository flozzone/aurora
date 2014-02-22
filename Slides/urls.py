from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^$', 'Slides.views.start', name="start"),
    url(r'^livecast/(?P<lecture_id_relative>\d+)/$', 'Slides.views.livecast', name="livecast"),
    url(r'^livecast_new_slide/(?P<course_id>\d+)/$', 'Slides.views.livecast_new_slide', name="livecast_new_slide"),
    url(r'^livecast/(?P<lecture_id_relative>\d+)/update_slide/(?P<slide_id>\d+)/(?P<client_timestamp>\d+)/json/$', 'Slides.views.livecast_update_slide', name="livecast_update_slide"),
    url(r'^studio/lecture/(?P<lecture_id_relative>\d+)/$', 'Slides.views.studio_lecture', name="studio_lecture"),
    url(r'^studio/confusing/$', 'Slides.views.studio_marker', {'marker': 'confusing'}, name="studio_confusing"),
    url(r'^studio/important/$', 'Slides.views.studio_marker', {'marker': 'important'}, name="studio_important"),
    url(r'^studio/liked/$', 'Slides.views.studio_marker', {'marker': 'liked'}, name="studio_liked"),
    url(r'^studio/search/$', 'Slides.views.studio_search', name="studio_search"),
    url(r'^mark_slide/(?P<slide_id>\d+)/(?P<marker>(liked|important|confusing))/(?P<value>(true|false|xxx))/json/$', 
        'Slides.views.mark_slide', name='mark_slide'),
)