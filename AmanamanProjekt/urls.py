from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from AmanamanProjekt.settings import MEDIA_ROOT
admin.autodiscover()

urlpatterns = patterns('',
                       # Examples:
                       url(r'^$', 'AmanamanProjekt.views.home', name='home'),
                       url(r'result_users', 'AmanamanProjekt.views.result_users', name='result_users'),
                       url(r'result_elabs_nonfinal', 'AmanamanProjekt.views.result_elabs_nonfinal', name='result_elabs_nonfinal'),
                       url(r'result_elabs_final', 'AmanamanProjekt.views.result_elabs_final', name='result_elabs_final'),
                       url(r'result_reviews', 'AmanamanProjekt.views.result_reviews', name='result_reviews'),
                       url(r'', include('PortfolioUser.urls')),
                       url(r'', include('Challenge.urls')),
                       url(r'', include('Elaboration.urls')),
                       url(r'', include('Evaluation.urls')),
                       url(r'', include('Review.urls')),
                       url(r'', include('FileUpload.urls')),
                       url(r'', include('Notification.urls')),
                       url(r'', include('Comments.urls', namespace='Comments')),
                       url(r'slides/', include('Slides.urls', namespace='Slides')),
                       # url(r'^AmanamanProjekt/', include('AmanamanProjekt.foo.urls')),

                       # Uncomment the admin/doc line below to enable admin documentation:
                       url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

                       # Uncomment the next line to enable the admin:
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
                            {'document_root': MEDIA_ROOT}),
)
