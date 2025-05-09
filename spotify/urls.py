from django.urls import path
from .views import *

urlpatterns = [
    path('get-auth-url', AuthURL.as_view()),
    path('redirect', spotify_callback),
    path('current-song', CurrentSong.as_view()),
    path('pause', PauseSong.as_view()),
    path('play', PlaySong.as_view()),
    path('active-device', ActiveDeviceView.as_view()),
    path('skip', SkipSong.as_view()),
    path('previous', PreviouSong.as_view()),
    path('check-authenticated', CheckSpotifyAuthenticated.as_view()),
]