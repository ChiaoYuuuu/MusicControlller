from spotify.infrastructure.client import fetch_current_song
from spotify.infrastructure.repository import get_room
from spotify.domain.service import build_song_response

def get_current_song(user_id, room_code):
    room = get_room(room_code)
    if not room:
        return {'data': {'error': 'Room not found'}, 'status': 404}
    song_data = fetch_current_song(user_id, room)
    if not song_data:
        return {'data': {}, 'status': 204}
    song_response = build_song_response(song_data, room)
    return {'data': song_response, 'status': 200} 