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
                       url(r'^profile/save/$', 'PortfolioUser.views.profile_save'),
                       url(r'^sso_auth_callback$', 'PortfolioUser.views.sso_auth_callback'),
)
