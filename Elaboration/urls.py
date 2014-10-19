from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^autosave/$', 'Elaboration.views.save_elaboration'),
    url(r'^create$', 'Elaboration.views.create_elaboration'),
)

