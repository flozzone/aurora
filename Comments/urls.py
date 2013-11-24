from django.conf.urls import url, patterns
from Comments.views import CommentList

urlpatterns = patterns(
    '',
    url(r'^feed/$', CommentList.as_view()),
)
