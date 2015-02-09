from django.conf.urls import url, patterns
from Comments import views

urlpatterns = patterns(
    '',
    url(r'^feed/$', views.feed, name='feed'),
    url(r'^bookmarks/$', views.bookmarks, name='bookmarks'),
    url(r'^post/$', views.post_comment, name='post'),
    url(r'^delete/$', views.delete_comment, name='delete'),
    url(r'^promote/$', views.promote_comment, name='promote'),
    url(r'^bookmark/$', views.bookmark_comment, name='bookmark'),
    url(r'^edit/$', views.edit_comment, name='edit'),
    url(r'^reply/$', views.post_reply, name='reply'),
    url(r'^vote/$', views.vote_on_comment, name='vote'),
    url(r'^update/$', views.update_comments, name='update'),
    url(r'^list_page/$', views.comment_list_page, name='list_page'),
    url(r'^mark_seen/$', views.mark_seen, name='mark_seen'),
    url(r'^autocomplete_tags/$', views.autocomplete_tags, name='autocomplete_tags'),
)
