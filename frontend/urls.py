from django.urls import path
from .views import index

app_name = 'frontend'

urlpatterns = [
    path('', index, name = ''),
    path('join', index),
    path('create', index),
    path('info', index),
    path('room/<str:roomCode>', index),
    path('register', index),
    path('login', index),
    path('logout', index),
    path('spotify-conflict', index),
    path('room-check/<str:roomCode>', index)
]
