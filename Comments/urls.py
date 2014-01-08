from django.conf.urls import url, patterns
from Comments import views

urlpatterns = patterns(
    '',
    url(r'^feed/$', views.feed, name='feed'),
    url(r'^post_comment/$', views.post_comment, name='post_comment'),
    url(r'^update_comment/$', views.update_comment, name='update_comment'),
    url(r'^test_template_tags/$', views.test_template_tags, name='test_template_tags'),
)
