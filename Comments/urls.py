from django.conf.urls import url, patterns
from Comments import views

urlpatterns = patterns(
    '',
    url(r'^feed/$', views.feed, name='feed'),
    url(r'^post_comment/$', views.post_comment, name='post_comment'),
    url(r'^post_reply/$', views.post_reply, name='post_reply'),
    url(r'^update_comments/$', views.update_comments, name='update_comments'),
    url(r'^test_template_tags/$', views.test_template_tags, name='test_template_tags'),
)
