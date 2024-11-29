from django.conf.urls import *
from signals import *
from django.conf import settings
from sysadmin.views import *
from setup.views import *
from utilities.views import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', index),
    url(r'^login/$', index),
    url(r'^header/$', header),
    url(r'^welcome/$', welcomecode),
    url(r'^online/$', online_result),
    url(r'^subject_report/$', subject_report),
    url(r'^student_search/$', search_student),
    url(r'^logout/$', logoutuser),
    url(r'^unauthorised/$', unatho),
    url(r'^uploadlga/$',uploadlocal ),
    url(r'^uploadsubgroup/$',uploadaccsubgrp),
    url(r'^uploadacc/$',uploadacc),
    url(r'^home_dashboard/$',dashboard),
    url(r'^uploadtransaction/$',uploadtransaction),
    url(r'^pass_change/$', change_password),
    url(r'^getchangepassword/$', getchangepassword),
    url(r'^uploadstudent/$',uploadstudent),
    url(r'^uploadbill/$',uploadbill),#to upload bill setup
    url(r'^uploadbillname/$',uploadbillname),#to upload bill name
    url(r'^uploadadditionalbill/$',uploadadditionalbill),#to upload  additional bills
    url(r'^uploadpostedbill/$',uploadpostedbill),#to upload posted bill

    url(r'^changepassword/$', changepassword),
    url(r'^setup/', include('setup.urls')),
    url(r'^student/', include('student.urls')),
    url(r'^bill/', include('bill.urls')),
    url(r'^cbt/', include('CBT.urls')),
    url(r'^sysadmin/', include('sysadmin.urls')),
    url(r'^controllers/', include('sysadmin.urls')),
    url(r'^assessment/', include('assessment.urls')),
    url(r'^reportsheet/', include('assessment.urls')),

    url(r'^lesson/', include('lesson.urls')),

    url(r'^assignment/', include('assignment.urls')),
   # url(r'^transport/', include('transport.urls')),
    url(r'^utils/', include('utilities.urls')),

    # url(r'^__debug__/', include(debug_toolbar.urls)),


    # Uncomment the admin/doc line below to enable admin documentation:
   # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),

    #url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)
