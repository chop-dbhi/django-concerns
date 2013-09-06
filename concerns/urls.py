from django.conf.urls import *

urlpatterns = patterns('concerns.views',
    url(r'^$', 'concern_list', name='concern-list'),
    url(r'^report/$', 'report_concern', name='report-concern'),
    url(r'^(?P<pk>\d+)/$', 'concern_detail', name='concern-detail'),
)
