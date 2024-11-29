
from django.conf.urls import patterns, url


urlpatterns = patterns('assignment.views',
    # Examples:
    url(r'^assignment/$', 'choose'),
    url(r'^t/pa/$', 'assignment'),
    url(r'^s/pj/$', 'studassign'),

    )
