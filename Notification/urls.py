from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^notifications$', 'Notification.views.notifications'),
    url(r'^notifications/read$', 'Notification.views.read'),
    url(r'^notifications/refresh$', 'Notification.views.refresh'),
)

