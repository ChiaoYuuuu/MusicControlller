from django.shortcuts import redirect
from .credentials import *
from rest_framework.views import APIView
from requests import Request, post
from rest_framework import status
from rest_framework.response import Response
from .util import *
from api.models import Room
from .models import SkipVote, PreviousVote
from rest_framework.permissions import IsAuthenticated, AllowAny 
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
import uuid
from django.core.cache import cache
from django.http import JsonResponse
import requests

class ActiveDeviceView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get(self, request, format=None):
        user_id = str(request.user.id)
        response = execute_spotify_api_request(user_id, "me/player/devices")
        #print("Spotify devices API response:", response)

        if response.get("Error"):
            return Response({'error': 'Failed to fetch devices'}, status=status.HTTP_400_BAD_REQUEST)

        active_devices = [d for d in response.get("devices", []) if d.get("is_active")]

        return Response({
            "active_device_exists": len(active_devices) > 0,
            "devices": response.get("devices", [])
        }, status=status.HTTP_200_OK)


class AuthURL(APIView):

    permission_classes = [IsAuthenticated] 
    def get(self, request, fornat=None):
        state = str(uuid.uuid4())
        cache.set(f"spotify_state_{state}", request.user.id, timeout=600)
        
        scopes = 'user-read-playback-state user-modify-playback-state user-read-currently-playing user-read-playback-state'
  
        url = Request('GET', 'https://accounts.spotify.com/authorize', params={
            'scope': scopes,
            'response_type': 'code',
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'state': state,
            'show_dialog': 'true'
        }).prepare().url

        return Response({'url': url}, status=status.HTTP_200_OK)


def clear_spotify_tokens(user_id):
    token = SpotifyToken.objects.filter(user=user_id).first()
    if token:
        token.access_token = ""
        token.refresh_token = ""
        token.token_type = ""
        token.expires_in = now()
        token.spotify_user_id = None
        token.save(update_fields=["access_token", "refresh_token", "token_type", "expires_in", "spotify_user_id"])



@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([AllowAny])
def spotify_callback(request):
    print("CALL BACK")
    code = request.GET.get("code")
    state = request.GET.get("state")
   
    user_id = cache.get(f"spotify_state_{state}")
    if user_id is None:
        raise AuthenticationFailed("Invalid or expired state value")
    

    response = post('https://accounts.spotify.com/api/token', data={
    'grant_type': 'authorization_code',
    'code': code,
    'redirect_uri': REDIRECT_URI,
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET
    })

    print("📥 Spotify token response:", response.status_code, response.text)

    # 防止 JSONDecodeError
    try:
        data = response.json()
    except ValueError:
        return JsonResponse({"error": "Failed to decode Spotify response", "raw": response.text}, status=500)

    access_token = data.get("access_token")
    refresh_token = data.get("refresh_token")
    token_type = data.get("token_type")
    expires_in = data.get("expires_in")

    headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
    }

    user_info_response = get("https://api.spotify.com/v1/me", headers=headers)

    print("🧾 Spotify /me response:", user_info_response.status_code, user_info_response.text)

    try:
        user_info = user_info_response.json()
    except ValueError:
        return JsonResponse({
            "error": "Failed to decode /v1/me response",
            "status_code": user_info_response.status_code,
            "response_text": user_info_response.text
        }, status=500)

    spotify_user_id = user_info.get("id")

    existing = SpotifyToken.objects.filter(spotify_user_id=spotify_user_id).exclude(user=user_id).first()
    if existing:
        print("existing")
        clear_spotify_tokens(user_id)
        return redirect(f"{settings.FRONTEND_URL}/spotify-conflict")
    print("update")
    update_or_create_spotify_tokens(
        str(user_id), str(spotify_user_id), access_token, token_type, expires_in, refresh_token
    )    
    
    return redirect('frontend:')


class CheckSpotifyAuthenticated(APIView):
    permission_classes = [IsAuthenticated]  

    def get(self, request, format=None):
        is_authenticated = is_spotify_authenticated(str(request.user.id))
        #return Response({"msg": "Stop here for debugging"}, status=200)
        return Response({'status': is_authenticated}, status=status.HTTP_200_OK)


class CurrentSong(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    def get(self, request, format=None):
        #print("Authenticated user: ", request.user)
        room_code = request.query_params.get('room_code')
        print("CurrentSong room : ", room_code)
        if not room_code:
            return Response({'error room code is required'}, status=status.HTTP_400_BAD_REQUEST)
        room = Room.objects.filter(code=room_code)
        if room.exists():
            print("room exist")
            room = room[0]
        else:
            print("room is not exist")
            return Response({}, status=status.HTTP_404_NOT_FOUND)

        host = str(request.user.id)
        endpoint = "player/currently-playing"
        response = execute_spotify_api_request(host, endpoint)
        print("1 RES : ", response, '\n\n\n')
        if 'error' in response or 'item' not in response:
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        playing_type = response.get('currently_playing_type')
        progress = response.get('progress_ms')
        is_playing = response.get('is_playing')
        skip_votes = SkipVote.objects.filter(room=room, song_id=room.current_song)
        previous_votes = PreviousVote.objects.filter(room=room, song_id=room.current_song)
        #print("SKIP : ", skip_votes)
        #print("PREVIOUS : ", previous_votes)
        
        if playing_type == "track":
            item = response.get('item')
            duration = item.get('duration_ms')
            album_cover = item.get('album').get('images')[0].get('url')
            song_id = item.get('id')
            #print("URL : ", album_cover)
            
            artist_string = ""

            for i, artist in enumerate(item.get('artists')):
                if i > 0:
                    artist_string += ", "
                name = artist.get('name')
                artist_string += name
            
            song = {
                'title': item.get('name'),
                'artist': artist_string,
                'duration': duration,
                'time': progress,
                'image_url': album_cover,
                'is_playing': is_playing,
                'skip_votes': len(skip_votes),
                'previous_votes': len(previous_votes),
                'votes_required' : room.votes_to_skip,
                'id': song_id
            }

        else:            
            endpoint = "player/queue"
            response = execute_spotify_api_request(host, endpoint)
            song_id = response.get('currently_playing').get('uri')
            #print('\n\n 2 RES : ', response.get('currently_playing'))
            song = {
                'title': response.get('currently_playing').get('name'),
                'artist': response.get('currently_playing').get('show').get('publisher'),
                'duration': response.get('currently_playing').get('duration_ms'),
                'time': progress,
                'image_url': response.get('currently_playing').get('show').get('images')[0].get('url'),
                'is_playing': is_playing,
                'skip_votes': len(skip_votes),
                'previous_votes': len(previous_votes),
                'votes_required' : room.votes_to_skip,
                'id': song_id
            }
            print("SONG : ", song)

        self.update_room_song(room, song_id)

        return Response(song, status=status.HTTP_200_OK)

    
    def update_room_song(self, room, song_id):
            current_song = room.current_song

            if current_song != song_id:
                room.current_song = song_id
                room.save(update_fields=['current_song'])
                skip_votes = SkipVote.objects.filter(room=room).delete()
                previous_votes = PreviousVote.objects.filter(room=room).delete()
    
class PauseSong(APIView):
    permission_classes = [IsAuthenticated]
    def put(self, request, format=None):
        room_code = request.data.get("room_code")
        if not room_code:
            return Response({'error': 'Room code is required'}, status=status.HTTP_400_BAD_REQUEST)
        room = Room.objects.filter(code=room_code).first()
        if not room:
            return Response({'error': 'Room not found for this user'}, status=status.HTTP_404_NOT_FOUND)
        if room.host == request.user or room.guest_can_pause:
            pause_song(room.host.id)
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        return Response({}, status=status.HTTP_403_FORBIDDEN)


class PlaySong(APIView):
    permission_classes = [IsAuthenticated]
    def put(self, request, format=None):
        user = request.user
        room_code = request.data.get("room_code")
        if not room_code:
            return Response({'error': 'Room code is required'}, status=status.HTTP_400_BAD_REQUEST)
        room = Room.objects.filter(code=room_code).first()
        if not room:
            return Response({'error': 'Room not found for this user'}, status=status.HTTP_404_NOT_FOUND)
        if room.host == user or room.guest_can_pause:
            play_song(room.host.id)
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        return Response({}, status=status.HTTP_403_FORBIDDEN)
    
class SkipSong(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        room_code = request.data.get("room_code")
        if not room_code:
            return Response({'error : room code is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        room = Room.objects.filter(code=room_code).first()
        if not room:
            return Response({'error : room is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        user_voted = SkipVote.objects.filter(
            user=request.user,
            room=room,
            song_id=room.current_song
        ).exists()

        votes = SkipVote.objects.filter(room=room, song_id=room.current_song)
        votes_needed = room.votes_to_skip

        print("Votes so far:", len(votes), "User already voted:", user_voted)
        if user_voted:
            if request.user == room.host or len(votes) >= votes_needed:
                votes.delete()
                skip_song(room.host.id)
                return Response({}, status.HTTP_204_NO_CONTENT)
            return Response({'message': 'Already voted'}, status=status.HTTP_200_OK)

        if request.user == room.host or len(votes) + 1 >= votes_needed:
            votes.delete()
            skip_song(room.host.id)
        else:
            vote = SkipVote(
                user=request.user,
                room=room,
                song_id=room.current_song
            )
            vote.save()

        return Response({}, status.HTTP_204_NO_CONTENT)

    
class PreviouSong(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        room_code = request.data.get("room_code")
        room = Room.objects.filter(code=room_code).first()
        user_voted = PreviousVote.objects.filter(
            user=request.user,
            room=room,
            song_id=room.current_song
        ).exists()

        votes = PreviousVote.objects.filter(room=room, song_id=room.current_song)
        votes_needed = room.votes_to_skip

        if user_voted:
            if request.user == room.host or len(votes) >= votes_needed:
                votes.delete()
                previous_song(room.host.id)
                return Response({}, status.HTTP_204_NO_CONTENT)
            return Response({'message': 'Already voted'}, status=status.HTTP_200_OK)

        if request.user == room.host or len(votes) + 1 >= votes_needed:
            votes.delete()
            previous_song(room.host.id)
        else:
            vote = PreviousVote(
                user=request.user,
                room=room,
                song_id=room.current_song
            )
            vote.save()

        return Response({}, status.HTTP_204_NO_CONTENT)
        
