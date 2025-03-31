from django.shortcuts import render, redirect
from .credentials import REDIRECT_URI, CLIENT_SECRET, CLIENT_ID
from rest_framework.views import APIView
from requests import Request, post
from rest_framework import status
from rest_framework.response import Response
from .util import *
from api.models import Room
from .models import SkipVote
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

class ActiveDeviceView(APIView):
    def get(self, request, format=None):
        if not request.session.exists(request.session.session_key):
            request.session.create()

        session_id = request.session.session_key

        if not session_id:
            return Response({'error': 'No session ID found'}, status=status.HTTP_401_UNAUTHORIZED)

        response = execute_spotify_api_request(session_id, "me/player/devices")
        #print("Spotify devices API response:", response)

        if response.get("Error"):
            return Response({'error': 'Failed to fetch devices'}, status=status.HTTP_400_BAD_REQUEST)

        active_devices = [d for d in response.get("devices", []) if d.get("is_active")]

        return Response({
            "active_device_exists": len(active_devices) > 0,
            "devices": response.get("devices", [])
        }, status=status.HTTP_200_OK)




class AuthURL(APIView):
    def get(self, request, fornat=None):
        scopes = 'user-read-playback-state user-modify-playback-state user-read-currently-playing user-read-playback-state'

        url = Request('GET', 'https://accounts.spotify.com/authorize', params={
            'scope': scopes,
            'response_type': 'code',
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID
        }).prepare().url

        return Response({'url': url}, status=status.HTTP_200_OK)


def spotify_callback(request, format=None):
    code = request.GET.get('code')

    response = post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }).json()
    #print('Test Response : ', response) 

    access_token = response.get('access_token')
    token_type = response.get('token_type')
    refresh_token = response.get('refresh_token')
    expires_in = response.get('expires_in')

    if not request.session.exists(request.session.session_key):
        request.session.create()

    update_or_create_user_tokens(
        request.session.session_key, access_token, token_type, expires_in, refresh_token)

    return redirect('frontend:')


class IsAuthenticated(APIView):
    def get(self, request, format=None):
        is_authenticated = is_spotify_authenticated(
            self.request.session.session_key)
        return Response({'status': is_authenticated}, status=status.HTTP_200_OK)


class CurrentSong(APIView):
    def ep_info(self, id):
        client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)  
        skibidi = sp.episode(id)
        #print('EP info : ', skibidi)

    def get(self, request, format=None):
        room_code = self.request.session.get('room_code')
        room = Room.objects.filter(code=room_code)
        if room.exists():
            room = room[0]
        else:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        host = room.host
        endpoint = "player/currently-playing"
        response = execute_spotify_api_request(host, endpoint)
        #print("1 RES : ", response, '\n\n\n')
        if 'error' in response or 'item' not in response:
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        playing_type = response.get('currently_playing_type')
        progress = response.get('progress_ms')
        is_playing = response.get('is_playing')
        
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

            votes = SkipVote.objects.filter(room=room, song_id=room.current_song)
            
            song = {
                'title': item.get('name'),
                'artist': artist_string,
                'duration': duration,
                'time': progress,
                'image_url': album_cover,
                'is_playing': is_playing,
                'votes': len(votes),
                'votes_required' : room.votes_to_skip,
                'id': song_id
            }

        else:            
            endpoint = "player/queue"
            response = execute_spotify_api_request(host, endpoint)

            votes = SkipVote.objects.filter(room=room, song_id=room.current_song)
            song_id = response.get('currently_playing').get('show').get('id')
            #print('\n\n 2 RES : ', response.get('currently_playing').get('show'))
            song = {
                'title': response.get('currently_playing').get('name'),
                'artist': response.get('currently_playing').get('show').get('publisher'),
                'duration': response.get('currently_playing').get('duration_ms'),
                'time': progress,
                'image_url': response.get('currently_playing').get('show').get('images')[0].get('url'),
                'is_playing': is_playing,
                'votes': len(votes),
                'votes_required' : room.votes_to_skip,
                'id': song_id
            }
            #print("SONG : ", song)

        self.update_room_song(room, song_id)

        return Response(song, status=status.HTTP_200_OK)
            
            

    
    def update_room_song(self, room, song_id):
            current_song = room.current_song

            if current_song != song_id:
                room.current_song = song_id
                room.save(update_fields=['current_song'])
                votes = SkipVote.objects.filter(room=room).delete()
    
class PauseSong(APIView):
    def put(self, request, format=None):
        room_code = request.session.get('room_code')
        room = Room.objects.filter(code=room_code)[0]
        if request.session.session_key == room.host or room.guest_can_pause:
            pause_song(room.host)
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        return Response({}, status=status.HTTP_403_FORBIDDEN)


class PlaySong(APIView):
    def put(self, request, format=None):
        room_code = request.session.get('room_code')
        room = Room.objects.filter(code=room_code)[0]
        if request.session.session_key == room.host or room.guest_can_pause:
            play_song(room.host)
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        return Response({}, status=status.HTTP_403_FORBIDDEN)
    
class SkipSong(APIView):
    def post(self, request, format=None):
        room_code = self.request.session.get('room_code')
        room = Room.objects.filter(code=room_code)[0]
        votes = SkipVote.objects.filter(room=room, song_id=room.current_song)
        votes_needed = room.votes_to_skip

        if self.request.session.session_key == room.host or len(votes) + 1 >= votes_needed:
            votes.delete()
            skip_song(room.host)
        else:
            vote = SkipVote(user=self.request.session.session_key,
                        room=room, song_id=room.current_song)
            vote.save()

        return Response({}, status.HTTP_204_NO_CONTENT)
    
class PreviouSong(APIView):
    def post(self, request, format=None):
        room_code = self.request.session.get('room_code')
        room = Room.objects.filter(code=room_code)[0]
        votes = SkipVote.objects.filter(room=room, song_id=room.current_song)
        votes_needed = room.votes_to_skip

        if self.request.session.session_key == room.host or len(votes) + 1 >= votes_needed:
            votes.delete()
            previous_song(room.host)
        else:
            vote = SkipVote(user=self.request.session.session_key,
                        room=room, song_id=room.current_song)
            vote.save()

        return Response({}, status.HTTP_204_NO_CONTENT)
