from .models import SpotifyToken
from django.utils import timezone
from datetime import timedelta
from .credentials import CLIENT_ID, CLIENT_SECRET
from requests import post, put, get
from django.utils.timezone import now


BASE_URL = "https://api.spotify.com/v1/me/"


def get_user_tokens(user_id):
    user_tokens = SpotifyToken.objects.filter(user=user_id)

    if user_tokens.exists():
        return user_tokens[0]
    else:
        return None


def update_or_create_spotify_tokens(user_id, spotify_user_id, access_token, token_type, expires_in, refresh_token):
    expires_at = now() + timedelta(seconds=expires_in)
    tokens = SpotifyToken.objects.filter(user=user_id).first()
    if tokens:
        tokens.access_token = access_token
        tokens.refresh_token = refresh_token
        tokens.expires_in = expires_at
        tokens.token_type = token_type
        tokens.save(update_fields=['access_token', 'refresh_token', 'expires_in', 'token_type'])
    else:
        tokens = SpotifyToken(
            user=user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            token_type=token_type,
            expires_in=expires_at, 
            spotify_user_id = spotify_user_id
        )
        tokens.save()


def is_spotify_authenticated(user_id):
    tokens = get_user_tokens(user_id)
    if tokens:
        expiry = tokens.expires_in
        if expiry <= timezone.now():
            print(f"Token refreshed for user {user_id}")
            refresh_spotify_token(user_id)

        return True
    return False


def refresh_spotify_token(user_id):
    token = get_user_tokens(user_id)
    if not token:
        print(f"Cannot refresh token: User token not exist  {user_id}")
        return
    spotify_user_id = token.spotify_user_id
    
    refresh_token = token.refresh_token
    if not refresh_token:
        print(f"Cannot refresh token: No token found for user {user_id}")
        return    

    response = post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }).json()

    access_token = response.get('access_token')
    token_type = response.get('token_type')
    expires_in = response.get('expires_in')

    update_or_create_spotify_tokens(
        user_id, spotify_user_id, access_token, token_type, expires_in, refresh_token)
    print(f"Refreshed token for user {user_id}")


def execute_spotify_api_request(user_id, endpoint, post_=False, put_=False):
    if not is_spotify_authenticated(user_id):
        return {"execute_spotify_api_request - error": "User not authenticated"}
    tokens = get_user_tokens(user_id)
    if not tokens:
        return {'Error': 'User not authenticated'}

    headers = {'Content-Type': 'application/json',
               'Authorization': "Bearer " + tokens.access_token}

    if post_:
        return post(BASE_URL + endpoint, headers=headers)
    if put_:
        return put(BASE_URL + endpoint, headers=headers)
    else:
        res = get(BASE_URL + endpoint, headers=headers)
        #print("Spotify API response : ", res.status_code, res.text)

    response = get(BASE_URL + endpoint, {}, headers=headers)
    #print('Response : ', response)
    #print('Text : ', response.text)
    #print("Endpoint:", BASE_URL + endpoint)
    #print("Headers:", headers)
    try:
        return response.json()
    except:
        return {'Error': 'Issue with request'}

    
def play_song(user_id):
    res = execute_spotify_api_request(user_id, "player/play", put_=True)
    print("🔁 Spotify play response:", res.status_code if hasattr(res, "status_code") else res)
    return res


def pause_song(user_id):
    res = execute_spotify_api_request(user_id, "player/pause", put_=True)
    return res


def skip_song(user_id):
    res = execute_spotify_api_request(user_id, "player/next", post_=True)
    print("Spotify skip response:", res.status_code if hasattr(res, "status_code") else res)
    return res


def previous_song(user_id):
    return execute_spotify_api_request(user_id, "player/previous", post_=True)