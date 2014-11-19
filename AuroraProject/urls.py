from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from AuroraProject.settings import MEDIA_ROOT
admin.autodiscover()

import AuroraProject.views

course_regex = r'^(?P<course>\w+)/'

urlpatterns = patterns('',
    # Examples:

    # TODO: add home without course

    # url reverse for javascript
    url(r'^jsreverse/$', 'django_js_reverse.views.urls_js', name='js_reverse'),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': MEDIA_ROOT}),


    url(r'result_users', 'AuroraProject.views.result_users', name='result_users'),
    url(r'result_elabs_nonfinal', 'AuroraProject.views.result_elabs_nonfinal', name='result_elabs_nonfinal'),
    url(r'result_elabs_final', 'AuroraProject.views.result_elabs_final', name='result_elabs_final'),
    url(r'result_reviews', 'AuroraProject.views.result_reviews', name='result_reviews'),

    url(r'^(?P<course>\w+)/', include(patterns('',
        url(r'^$', AuroraProject.views.home, name='home'),
        url(r'^challenge/', include('Challenge.urls', namespace='Challenge')),
        url(r'^elaboration/', include('Elaboration.urls')),
        url(r'^review/', include('Review.urls')),
        url(r'', include('Evaluation.urls')),
        url(r'', include('AuroraUser.urls', namespace='user')),
        ))),

    url(r'', include('FileUpload.urls')),
    url(r'', include('Notification.urls')),
    url(r'', include('Comments.urls', namespace='Comments')),
    url(r'slides/', include('Slides.urls', namespace='Slides')),
    # url(r'^AuroraProject/', include('AuroraProject.foo.urls')),

)
