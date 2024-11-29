
from django.conf.urls import patterns, url

urlpatterns = patterns('CBT.views',

    url(r'^home/$', 'chroose'),
    url(r'^set_user/subject/$', 'assignment'),
    url(r'^set_paper/active/$', 'cbtstat'),

    ###****questions************
    url(r'^enter/question/$', 'qstn'),
    # url(r'^enter/question/$', 'ajaxclassp'),
    url(r'^enter/ajaxclass/$', 'ajaxclass'),
    url(r'^getcbtsubject/$', 'getcbtsubject'),
    url(r'^enter/question/getqstn/$', 'getcbtqst'),

    url(r'^enter/question/ajax/$', 'editcbtqst'),


##*******options *******************
    url(r'^enter/options/getopt/$', 'getcbtopt'),
    url(r'^options/$', 'options'),
    url(r'^options/options/(\d+)/$', 'myoptions'),
    url(r'^options/enteropt/$', 'optajax'),

#***--------------theory------------------
    url(r'^enter/theory/$', 'theory'),

    ##****** student's view**************
    url(r'^cbt/exam/$', 'exxxam'),
    url(r'^take_test/start/$', 'pupilcbt'),
    url(r'^take_test/next/$', 'next'),
    url(r'^take_test/clear/$', 'clear'),
    url(r'^take_test/previous/$', 'beefore'),


    ##*******edit *******************
    url(r'^enter/options/edit/$', 'editquestion'),
    url(r'^edit/$', 'editq'),
    url(r'^options/options/(\d+)/$', 'myoptions'),
    url(r'^edit/editentry/$', 'doentry'),

    )
