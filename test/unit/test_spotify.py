from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User
import uuid
from spotify.infrastructure import client as spotify_client
from unittest.mock import patch, MagicMock
from django.utils import timezone
from datetime import timedelta
from api.infrastructure.models import Room

class SpotifyControllerTestCase(APITestCase):
    def setUp(self):
        self.username = f"testuser_{uuid.uuid4().hex[:8]}"
        self.password = "testpass"
        self.user = User.objects.create_user(username=self.username, password=self.password)
        login_resp = self.client.post('/api/login', {'username': self.username, 'password': self.password}, format='json')
        self.access_token = login_resp.data['access']
        self.auth_header = {'HTTP_AUTHORIZATION': f'Bearer {self.access_token}'}

    def test_current_song_unauthorized(self):
        response = self.client.get('/spotify/current-song')
        self.assertEqual(response.status_code, 401)

    def test_current_song_no_room(self):
        response = self.client.get('/spotify/current-song', **self.auth_header)
        self.assertIn(response.status_code, [400, 404, 204])

    def test_active_device(self):
        response = self.client.get('/spotify/active-device', **self.auth_header)
        self.assertIn(response.status_code, [200, 400])

    def test_check_authenticated(self):
        response = self.client.get('/spotify/check-authenticated', **self.auth_header)
        self.assertEqual(response.status_code, 200)
        self.assertIn('status', response.data)

    def test_skip_song_no_room(self):
        response = self.client.post('/spotify/skip', {'room_code': 'notexist'}, format='json', **self.auth_header)
        self.assertIn(response.status_code, [400, 404])

    def test_skip_song_data_missing(self):
        response = self.client.post('/spotify/skip', {}, format='json', **self.auth_header)
        self.assertEqual(response.status_code, 400)

    def test_play_song_no_room(self):
        response = self.client.put('/spotify/play', {'room_code': 'notexist'}, format='json', **self.auth_header)
        self.assertIn(response.status_code, [400, 404])

    def test_pause_song_no_room(self):
        response = self.client.put('/spotify/pause', {'room_code': 'notexist'}, format='json', **self.auth_header)
        self.assertIn(response.status_code, [400, 404])

    def test_previous_song_no_room(self):
        response = self.client.post('/spotify/previous', {'room_code': 'notexist'}, format='json', **self.auth_header)
        self.assertIn(response.status_code, [400, 404])

    def test_auth_url(self):
        response = self.client.get('/spotify/get-auth-url', **self.auth_header)
        self.assertEqual(response.status_code, 200)
        self.assertIn('url', response.data)

    # 你可以根據實際情境補充更多正常流程（如建立房間後再操作）

    def test_current_song_endpoint(self):
        url = '/spotify/current-song'  # 直接用路徑
        response = self.client.get(url, **self.auth_header)
        self.assertIn(response.status_code, [200, 204, 400, 404])

    def test_skip_song_vote(self):
        # 先建立房間
        create_room_url = '/api/create-room'
        room_data = {'guest_can_pause': True, 'votes_to_skip': 2}
        create_resp = self.client.post(create_room_url, room_data, format='json', **self.auth_header)
        self.assertIn(create_resp.status_code, [200, 201])
        room_code = create_resp.data.get('code')
        # 投票 skip song
        skip_url = '/spotify/skip'
        vote_data = {'room_code': room_code}
        response = self.client.post(skip_url, vote_data, format='json', **self.auth_header)
        self.assertIn(response.status_code, [200, 204, 400, 404])

    def test_skip_song_invalid_room(self):
        skip_url = '/spotify/skip'
        vote_data = {'room_code': 'notexist'}
        response = self.client.post(skip_url, vote_data, format='json', **self.auth_header)
        self.assertIn(response.status_code, [400, 404])

class SpotifyClientUnitTest(APITestCase):
    def setUp(self):
        self.username = f"user_{uuid.uuid4().hex[:8]}"
        self.password = "testpass"
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.user_id = str(self.user.id)
        self.token = spotify_client.SpotifyToken.objects.create(
            user=self.user_id,
            access_token='token',
            refresh_token='refresh',
            token_type='Bearer',
            expires_in=timezone.now() + timedelta(seconds=3600),
            spotify_user_id='spid'
        )
        self.room = Room.objects.create(
            code=uuid.uuid4().hex[:8],
            host=self.user,
            guest_can_pause=True,
            votes_to_skip=2,
            current_song='songid'
        )

    def test_get_user_tokens_exists(self):
        token = spotify_client.get_user_tokens(self.user_id)
        self.assertIsNotNone(token)

    def test_get_user_tokens_not_exists(self):
        token = spotify_client.get_user_tokens('not_exist')
        self.assertIsNone(token)

    @patch('spotify.infrastructure.client.refresh_spotify_token')
    def test_is_spotify_authenticated_expired(self, mock_refresh):
        self.token.expires_in = timezone.now() - timedelta(seconds=10)
        self.token.save()
        result = spotify_client.is_spotify_authenticated(self.user_id)
        self.assertTrue(result)
        mock_refresh.assert_called_once()

    def test_is_spotify_authenticated_no_token(self):
        result = spotify_client.is_spotify_authenticated('not_exist')
        self.assertFalse(result)

    @patch('spotify.infrastructure.client.get_user_tokens')
    @patch('spotify.infrastructure.client.post')
    def test_refresh_spotify_token_success(self, mock_post, mock_get):
        mock_token = MagicMock()
        mock_token.refresh_token = 'refresh'
        mock_token.spotify_user_id = 'spid'
        mock_get.return_value = mock_token
        mock_post.return_value.json.return_value = {
            'access_token': 'new_token', 'token_type': 'Bearer', 'expires_in': 3600
        }
        spotify_client.update_or_create_spotify_tokens = MagicMock()
        spotify_client.refresh_spotify_token(self.user_id)
        spotify_client.update_or_create_spotify_tokens.assert_called_once()

    def test_refresh_spotify_token_no_token(self):
        spotify_client.refresh_spotify_token('not_exist')

    @patch('spotify.infrastructure.client.is_spotify_authenticated', return_value=False)
    def test_execute_spotify_api_request_not_authenticated(self, mock_auth):
        result = spotify_client.execute_spotify_api_request(self.user_id, 'endpoint')
        self.assertIn('error', str(result).lower())

    @patch('spotify.infrastructure.client.is_spotify_authenticated', return_value=True)
    @patch('spotify.infrastructure.client.get_user_tokens')
    @patch('spotify.infrastructure.client.get')
    def test_execute_spotify_api_request_get(self, mock_get, mock_get_tokens, mock_auth):
        mock_token = MagicMock()
        mock_token.access_token = 'token'
        mock_get_tokens.return_value = mock_token
        mock_get.return_value.json.return_value = {'ok': True}
        result = spotify_client.execute_spotify_api_request(self.user_id, 'endpoint')
        self.assertEqual(result, {'ok': True})

    @patch('spotify.infrastructure.client.is_spotify_authenticated', return_value=True)
    @patch('spotify.infrastructure.client.get_user_tokens')
    @patch('spotify.infrastructure.client.post')
    def test_execute_spotify_api_request_post(self, mock_post, mock_get_tokens, mock_auth):
        mock_token = MagicMock()
        mock_token.access_token = 'token'
        mock_get_tokens.return_value = mock_token
        mock_post.return_value = MagicMock()
        result = spotify_client.execute_spotify_api_request(self.user_id, 'endpoint', post_=True)
        self.assertIsNotNone(result)

    @patch('spotify.infrastructure.client.is_spotify_authenticated', return_value=True)
    @patch('spotify.infrastructure.client.get_user_tokens')
    @patch('spotify.infrastructure.client.put')
    def test_execute_spotify_api_request_put(self, mock_put, mock_get_tokens, mock_auth):
        mock_token = MagicMock()
        mock_token.access_token = 'token'
        mock_get_tokens.return_value = mock_token
        mock_put.return_value = MagicMock()
        result = spotify_client.execute_spotify_api_request(self.user_id, 'endpoint', put_=True)
        self.assertIsNotNone(result)

    @patch('spotify.infrastructure.client.execute_spotify_api_request')
    def test_play_song(self, mock_exec):
        mock_exec.return_value = {'ok': True}
        result = spotify_client.play_song(self.user_id)
        self.assertEqual(result, {'ok': True})

    @patch('spotify.infrastructure.client.execute_spotify_api_request')
    def test_pause_song(self, mock_exec):
        mock_exec.return_value = {'ok': True}
        result = spotify_client.pause_song(self.user_id)
        self.assertEqual(result, {'ok': True})

    @patch('spotify.infrastructure.client.execute_spotify_api_request')
    def test_skip_song(self, mock_exec):
        mock_exec.return_value = MagicMock(status_code=204)
        result = spotify_client.skip_song(self.user_id)
        self.assertIsNotNone(result)

    @patch('spotify.infrastructure.client.execute_spotify_api_request')
    def test_previous_song(self, mock_exec):
        mock_exec.return_value = {'ok': True}
        result = spotify_client.previous_song(self.user_id)
        self.assertEqual(result, {'ok': True})

    @patch('spotify.infrastructure.client.execute_spotify_api_request')
    def test_fetch_current_song_success(self, mock_exec):
        mock_exec.return_value = {'item': {'name': 'n', 'artists': [], 'duration_ms': 1, 'album': {}, 'id': 'songid'}, 'is_playing': True}
        result = spotify_client.fetch_current_song(self.user_id, self.room)
        self.assertIsInstance(result, dict)

    @patch('spotify.infrastructure.client.execute_spotify_api_request')
    def test_fetch_current_song_fail(self, mock_exec):
        mock_exec.return_value = {'error': 'fail'}
        result = spotify_client.fetch_current_song(self.user_id, self.room)
        self.assertIsNone(result) 