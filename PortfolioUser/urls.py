from django.conf.urls import patterns, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^login/$', 'PortfolioUser.views.login'),
                       url(r'^signin/$', 'PortfolioUser.views.signin'),
                       url(r'^signout/$', 'PortfolioUser.views.signout'),
                       url(r'^course/$', 'PortfolioUser.views.course'),
                       url(r'^profile/$', 'PortfolioUser.views.profile'),
)



