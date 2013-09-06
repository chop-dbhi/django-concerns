from django.conf.urls import patterns, url, include

urlpatterns = patterns('',
    url(r'^concerns/', include('concerns.urls')),
)
