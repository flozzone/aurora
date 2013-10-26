from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'AmanamanProjekt.views.home', name='home'),
    url(r'^login/$', 'PortfolioUser.views.login'),
    url(r'^signin/$', 'PortfolioUser.views.signin'),
    url(r'^signout/$', 'PortfolioUser.views.signout'),
    url(r'', include('Challenge.urls')),

    # url(r'^AmanamanProjekt/', include('AmanamanProjekt.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
