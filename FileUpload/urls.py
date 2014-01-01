from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^fileupload$', 'FileUpload.views.file_upload'),
)