from django.conf.urls import patterns, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^login/$', 'AuroraUser.views.login'),
                       url(r'^signin/$', 'AuroraUser.views.signin'),
                       url(r'^signout/$', 'AuroraUser.views.signout'),
                       url(r'^course/$', 'AuroraUser.views.course'),
                       url(r'^profile/$', 'AuroraUser.views.profile'),
                       url(r'^profile/save/$', 'AuroraUser.views.profile_save'),
                       url(r'^sso_auth_callback$', 'AuroraUser.views.sso_auth_callback'),
)
