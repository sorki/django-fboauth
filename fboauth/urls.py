from django.conf.urls.defaults import *

from views import start, complete

urlpatterns = patterns('',
    url(r'start/$', 
        start,
        name='fboauth_start'),
    url(r'complete/$', 
        complete, 
        name='fboauth_complete'),
    )


