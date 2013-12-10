from django.conf.urls import url, patterns
from Comments import views

urlpatterns = patterns(
    '',
    url(r'^feed/$', views.CommentList.as_view(), name='feed'),
    url(r'^post/$', views.post_comment, name='post_comment'),
    url(r'^test_template_tags/$', views.test_template_tags, name='test_template_tags'),
)
