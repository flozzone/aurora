from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^challenges/submit$', 'Elaboration.views.submit_elaboration'),
    url(r'^challenges/autosave/$', 'Elaboration.views.save_elaboration'),
)

