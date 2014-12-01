from django.conf.urls import patterns, url
import Notification.views

urlpatterns = patterns('',
                       url(r'^$', 'Notification.views.notifications'),
                       url(r'^write$', 'Notification.views.write_notification'),
                       url(r'^send$', 'Notification.views.send_notification'),
                       url(r'^read$', 'Notification.views.read'),
                       url(r'^refresh$', Notification.views.refresh, name='notifications'),
                       )

