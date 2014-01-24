from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
                       # Examples:
                       url(r'^$', 'AmanamanProjekt.views.home', name='home'),
                       url(r'', include('PortfolioUser.urls')),
                       url(r'', include('Challenge.urls')),
                       url(r'', include('Elaboration.urls')),
                       url(r'', include('Evaluation.urls')),
                       url(r'', include('Review.urls')),
                       url(r'', include('FileUpload.urls')),
                       url(r'', include('Comments.urls', namespace='Comments')),
                       url(r'slides/', include('Slides.urls', namespace='Slides')),
                       # url(r'^AmanamanProjekt/', include('AmanamanProjekt.foo.urls')),

                       # Uncomment the admin/doc line below to enable admin documentation:
                       url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

                       # Uncomment the next line to enable the admin:
                       url(r'^admin/', include(admin.site.urls)),
)
