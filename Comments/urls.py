from django.conf.urls import url, patterns
from Comments import views

urlpatterns = patterns(
    '',
    url(r'^feed/$', views.CommentList.as_view(), name='feed'),
    url(r'^post/$', views.post, name='post'),
)
