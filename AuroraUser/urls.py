from django.conf.urls import patterns, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from AuroraUser import views

admin.autodiscover()

urlpatterns = patterns('',
                       # namespace comes from main urls.py
                       url(r'^login/$', views.login, name='login'),
                       url(r'^signin/$', views.signin, name='signin'),
                       url(r'^signout/$', views.signout, name='signout'),
                       url(r'^course/$', 'AuroraUser.views.course'),
                       url(r'^profile/$', views.profile, name='profile'),
                       url(r'^profile/save/$', views.profile_save, name='save'),
                       url(r'^sso_auth_callback$', 'AuroraUser.views.sso_auth_callback'),
                       )
