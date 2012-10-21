from django.conf.urls import patterns, include, url

urlpatterns = patterns('frontend.views',
    url(r'^$', 'index', name='index'),
    url(r'^register/$', 'register', name='register'),
    url(r'^login/$', 'login', name='login'),
    url(r'^logout/$', 'logout', name='logout'),
    url(r'^play/$', 'begin', name='begin'),
    url(r'^play/(?P<session_id>\d+)/$', 'resume', name='resume'),
    url(r'^profile/$', 'preferences', name='preferences'),
    url(r'^profile/(?P<player_id>\d+)/$', 'profile', name='profile'),
)