from rest_framework import generics, status
from .serializers import RoomSerializer, CreateRoomSerializer, UpdateRoomSerializer
from .models import Room, TopCharts
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated 
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import json
from django.utils import timezone
from datetime import timedelta
from django.core.cache import cache
from django.db import transaction, IntegrityError

class TopSong(APIView):
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        country_codes = ["TW", "JP", "KR", "US"]
        result = {}
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)

        for code in country_codes:
            today_latest = (
                TopCharts.objects.using('oracle')
                .filter(country_code=code, retrieved_at__date=today)
                .order_by('-retrieved_at')
                .values_list('retrieved_at', flat=True)
                .first()
            )

            yesterday_latest = (
                TopCharts.objects.using('oracle')
                .filter(country_code=code, retrieved_at__date=yesterday)
                .order_by('-retrieved_at')
                .values_list('retrieved_at', flat=True)
                .first()
            )

            today_songs = []
            if today_latest:
                today_songs = list(
                    TopCharts.objects.using('oracle')
                    .filter(country_code=code, retrieved_at=today_latest)
                    .order_by('rank')[:10]
                    .values('track_id', 'song_name', 'artist_name', 'rank')
                )

            yesterday_songs_map = {}
            if yesterday_latest:
                yesterday_songs_map = {
                    song['track_id']: song['rank']
                    for song in TopCharts.objects.using('oracle')
                    .filter(country_code=code, retrieved_at=yesterday_latest)
                    .values('track_id', 'rank')
                }

            for song in today_songs:
                track_id = song['track_id']
                current_rank = song['rank']
                prev_rank = yesterday_songs_map.get(track_id)

                if prev_rank is None:
                    song['rank_change'] = 'NEW'
                else:
                    diff = prev_rank - current_rank
                    if diff > 0:
                        song['rank_change'] = f'↑{diff}'
                    elif diff < 0:
                        song['rank_change'] = f'↓{abs(diff)}'
                    else:
                        song['rank_change'] = '-'

            result[code] = today_songs

        return Response(result)

class TokenRefresh(APIView):
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh = RefreshToken(refresh_token)
            new_access = str(refresh.access_token)
            return Response({"access": new_access}, status=status.HTTP_200_OK)
        except TokenError:
            return Response({"error": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username 
        token['user_id'] = user.id
        return token

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class AutoLeave(APIView):
    permission_classes = [AllowAny]  

    def post(self, request, format=None):
        try:
            body = json.loads(request.body)
            room_code = body.get("room_code")
            room = Room.objects.filter(code=room_code).first()
            if room:
                room.delete()
        except Exception as e:
            print("leave-room error:", e)
        print("LEAVE ROOM SUCCESS")
        return Response({"message": "Left room"}, status=status.HTTP_200_OK)

class Login(APIView):
    def post(self, request):
        
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({'error': 'Username and password required'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            refresh["user_id"] = user.id
            refresh["username"] = user.username
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'username': user.username
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class RegisterView(APIView):
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({"error": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.create_user(username=username, password=password)
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "User registered successfully",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }, status=status.HTTP_201_CREATED)

        except IntegrityError:
            return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
class RoomView(generics.ListAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

class GetRoom(APIView):
    serializer_class = RoomSerializer
    lookup_url_kwarg = 'code'
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        
        code = request.GET.get(self.lookup_url_kwarg)
        if code != None:
            room = Room.objects.filter(code=code)
            if len(room) > 0:
                data = RoomSerializer(room[0]).data
                data['is_host'] = request.user == room[0].host
                print("GetRoom : \n Resquest.user : ", request.user, "\nRoom[0].host : ", room[0].host)
                print("data['is_host'] :", data['is_host'])
                return Response(data, status=status.HTTP_200_OK)
            return Response({'Room Not Found': 'Invalid Room Code.'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'Bad Request': 'Code paramater not found in request'}, status=status.HTTP_400_BAD_REQUEST)

class JoinRoom(APIView):
    lookup_url_kwarg = 'code'
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        code = request.data.get(self.lookup_url_kwarg)
        if code != None:
            room_result = Room.objects.filter(code=code)
            if room_result.exists():
                return Response({'message': 'Room Joined!'}, status=status.HTTP_200_OK)

            return Response({'Bad Request': 'Invalid Room Code'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'Bad Request': 'Invalid post data, did not find a code key'}, status=status.HTTP_400_BAD_REQUEST)

class CreateRoomView(APIView):
    serializer_class = CreateRoomSerializer
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'error': 'Invalid data.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        guest_can_pause = serializer.validated_data['guest_can_pause']
        votes_to_skip    = serializer.validated_data['votes_to_skip']
        host             = request.user
        cache_key        = f"user_room_{host.id}"

        room, created = Room.objects.update_or_create(
            host=host,
            defaults={
                'guest_can_pause': guest_can_pause,
                'votes_to_skip': votes_to_skip,
            }
        )

        cache.set(cache_key, room, timeout=600)
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(
            RoomSerializer(room).data,
            status=status_code
        )
 
class UserInRoom(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        room = Room.objects.filter(host=request.user).first()
        return JsonResponse({'code': room.code if room else None}, status=status.HTTP_200_OK)
    
class LeaveRoom(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, format=None):
        user = request.user
        cache_key = f"user_room_{user.id}"

        room = Room.objects.select_for_update().filter(host=user).first()
        if room:
            room.delete()
            cache.delete(cache_key)

        return Response({'message': 'Success'}, status=status.HTTP_200_OK)


    
class UpdateRoom(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UpdateRoomSerializer

    def patch(self, request, format=None):

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            guest_can_pause = serializer.data.get('guest_can_pause')
            votes_to_skip = serializer.data.get('votes_to_skip')
            code = serializer.data.get('code')

            queryset = Room.objects.filter(code=code)
            if not queryset.exists():
                return Response({'msg': 'Room not found.'}, status=status.HTTP_404_NOT_FOUND)

            room = queryset[0]
            user_id = request.user
            if room.host != user_id:
                return Response({'msg': 'You are not the host of this room.'}, status=status.HTTP_403_FORBIDDEN)

            room.guest_can_pause = guest_can_pause
            room.votes_to_skip = votes_to_skip
            room.save(update_fields=['guest_can_pause', 'votes_to_skip'])
            return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)

        return Response({'Bad Request': "Invalid Data..."}, status=status.HTTP_400_BAD_REQUEST)