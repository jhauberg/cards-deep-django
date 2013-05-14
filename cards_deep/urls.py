from django.conf.urls import patterns, url

urlpatterns = patterns(
    'frontend.views',
    url(r'^$', 'index', name='index'),
    url(r'^register/$', 'register', name='register'),
    url(r'^login/$', 'login', name='login'),
    url(r'^login/$', 'login', name='login_as_guest'),
    url(r'^logout/$', 'logout', name='logout'),
    url(r'^play/$', 'begin', name='begin'),
    url(r'^play/(?P<session_id>\d+)/$', 'resume', name='resume'),
    url(r'^play/(?P<session_id>\d+)/card$', 'card', name='card'),
    url(r'^profile/$', 'preferences', name='preferences'),
    url(r'^profile/(?P<player_id>\d+)/$', 'profile', name='profile'),
)

urlpatterns += patterns(
    'core.views',
    url(r'^play/(?P<session_id>\d+)/state/$', view='state', name='state'),
    url(r'^play/(?P<session_id>\d+)/action/(?P<action_type>\w+)/$', view='perform_action', name='perform_action'),
)
