from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^fileupload$', 'FileUpload.views.file_upload'),
    url(r'^fileupload/all$', 'FileUpload.views.all_files'),
    url(r'^fileupload/remove$', 'FileUpload.views.file_remove'),
)