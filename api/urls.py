from django.urls import path
from .views import *

urlpatterns = [
    path('room', RoomView.as_view()),
    path('create-room', CreateRoomView.as_view()),
    path('get-room', GetRoom.as_view()), 
    path('join-room', JoinRoom.as_view()),
    path('user-in-room', UserInRoom.as_view()),
    path('leave-room', LeaveRoom.as_view()),
    path('update-room', UpdateRoom.as_view()),
    path('register', RegisterView.as_view(), name='api_register'),
    path('login', Login.as_view(), name='api_login'),
    path('token', MyTokenObtainPairView.as_view(), name='token'),
    path('token-refresh', TokenRefresh.as_view(), name='token_refresh'),
    path('auto-leave', AutoLeave.as_view(), name='auto_leave'),
   
]