from django.conf.urls import patterns, url

urlpatterns = patterns('',
                       url(r'^notifications$', 'Notification.views.notifications'),
                       url(r'^notifications/write$', 'Notification.views.write_notification'),
                       url(r'^notifications/send$', 'Notification.views.send_notification'),
                       url(r'^notifications/read$', 'Notification.views.read'),
                       url(r'^notifications/refresh$', 'Notification.views.refresh'),
)

