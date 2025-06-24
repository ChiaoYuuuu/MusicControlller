from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
import uuid
from spotify.application.player_application import get_current_song
from unittest.mock import patch, MagicMock
from spotify.domain.service import build_song_response
from api.config.exception_handler import custom_exception_handler
from rest_framework.response import Response
from api.domain.service.auth_service import AuthService

# Create your tests here.

class JWTAuthAPITestCase(APITestCase):
    def setUp(self):
        # 註冊唯一用戶
        self.username = f"testuser_{uuid.uuid4().hex[:8]}"
        register_url = '/api/register'
        register_data = {'username': self.username, 'password': 'testpass'}
        self.client.post(register_url, register_data, format='json')
        # 登入取得 access token
        login_url = '/api/login'
        login_data = {'username': self.username, 'password': 'testpass'}
        login_resp = self.client.post(login_url, login_data, format='json')
        self.access_token = login_resp.data['access']
        self.auth_header = {'HTTP_AUTHORIZATION': f'Bearer {self.access_token}'}

    def test_create_room(self):
        url = '/api/create-room'
        data = {'guest_can_pause': True, 'votes_to_skip': 2}
        response = self.client.post(url, data, format='json', **self.auth_header)
        print('create_room:', response.status_code, response.data)
        self.assertIn(response.status_code, [200, 201])
        self.assertIn('code', response.data)

    def test_get_room(self):
        # 先建立房間
        create_url = '/api/create-room'
        data = {'guest_can_pause': True, 'votes_to_skip': 2}
        create_resp = self.client.post(create_url, data, format='json', **self.auth_header)
        code = create_resp.data.get('code')
        url = f'/api/get-room?code={code}'
        response = self.client.get(url, **self.auth_header)
        print('get_room:', response.status_code, response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['code'], code)

    def test_join_room(self):
        # 先建立房間
        create_url = '/api/create-room'
        data = {'guest_can_pause': True, 'votes_to_skip': 2}
        create_resp = self.client.post(create_url, data, format='json', **self.auth_header)
        code = create_resp.data.get('code')
        url = '/api/join-room'
        response = self.client.post(url, {'code': code}, format='json', **self.auth_header)
        print('join_room:', response.status_code, response.data)
        self.assertEqual(response.status_code, 200)

    def test_leave_room(self):
        create_url = '/api/create-room'
        data = {'guest_can_pause': True, 'votes_to_skip': 2}
        create_resp = self.client.post(create_url, data, format='json', **self.auth_header)
        code = create_resp.data.get('code')
        url = '/api/leave-room'
        response = self.client.post(url, {'room_code': code}, format='json', **self.auth_header)
        print('leave_room:', response.status_code, response.data)
        self.assertEqual(response.status_code, 200)

    def test_update_room(self):
        create_url = '/api/create-room'
        data = {'guest_can_pause': True, 'votes_to_skip': 2}
        create_resp = self.client.post(create_url, data, format='json', **self.auth_header)
        code = create_resp.data.get('code')
        url = '/api/update-room'
        update_data = {'code': code, 'guest_can_pause': False, 'votes_to_skip': 3}
        response = self.client.patch(url, update_data, format='json', **self.auth_header)
        print('update_room:', response.status_code, response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['votes_to_skip'], 3)

    def test_user_in_room(self):
        create_url = '/api/create-room'
        data = {'guest_can_pause': True, 'votes_to_skip': 2}
        self.client.post(create_url, data, format='json', **self.auth_header)
        url = '/api/user-in-room'
        response = self.client.get(url, **self.auth_header)
        print('user_in_room:', response.status_code, response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('code', response.data)

    def test_token_refresh(self):
        # 登入取得 refresh token
        login_url = '/api/login'
        login_data = {'username': self.username, 'password': 'testpass'}
        login_resp = self.client.post(login_url, login_data, format='json')
        refresh_token = login_resp.data['refresh']
        url = '/api/token-refresh'
        response = self.client.post(url, {'refresh': refresh_token}, format='json')
        print('token_refresh:', response.status_code, response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)

    def test_register_and_login(self):
        username = f"newuser_{uuid.uuid4().hex[:8]}"
        register_url = '/api/register'
        data = {'username': username, 'password': 'newpass'}
        reg_resp = self.client.post(register_url, data, format='json')
        print('register:', reg_resp.status_code, reg_resp.data)
        self.assertEqual(reg_resp.status_code, 201)
        login_url = '/api/login'
        login_resp = self.client.post(login_url, data, format='json')
        print('login:', login_resp.status_code, login_resp.data)
        self.assertEqual(login_resp.status_code, 200)
        self.assertIn('access', login_resp.data)

    def test_top_song(self):
        url = '/api/top-song'
        response = self.client.get(url)
        print('top_song:', response.status_code, response.data)
        self.assertEqual(response.status_code, 200)

    def test_auto_leave(self):
        # 先建立房間
        create_url = '/api/create-room'
        data = {'guest_can_pause': True, 'votes_to_skip': 2}
        create_resp = self.client.post(create_url, data, format='json', **self.auth_header)
        code = create_resp.data.get('code')
        url = '/api/auto-leave'
        response = self.client.post(url, {'room_code': code}, format='json')
        print('auto_leave:', response.status_code, response.data)
        self.assertIn(response.status_code, [200, 404])

class ApplicationDomainTestCase(APITestCase):
    def test_get_current_song_no_room(self):
        result = get_current_song('some_user_id', 'notexist')
        self.assertEqual(result['status'], 404)

    @patch('spotify.infrastructure.client.execute_spotify_api_request')
    def test_fetch_current_song_api_error(self, mock_api):
        from spotify.infrastructure.client import fetch_current_song
        mock_api.return_value = {'error': 'fail'}
        class MockRoom:
            current_song = 'abc'
        result = fetch_current_song('uid', room=MockRoom())
        self.assertIsNone(result)

    def test_build_song_response_artist_string(self):
        class MockRoom:
            votes_to_skip = 2
        song_data = {
            'name': 'A',
            'artists': [{'name': 'X'}, {'name': 'Y'}],
            'duration_ms': 100,
            'album': {'images': [{'url': 'u'}]},
            'is_playing': True,
            'id': 'id',
            'skip_votes': [1, 2],
        }
        room = MockRoom()
        result = build_song_response(song_data, room)
        self.assertEqual(result['artist'], 'X, Y')

class ExceptionHandlerTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_validation_error(self):
        # 測試註冊時缺少密碼，應回傳 400
        response = self.client.post('/api/register', {'username': 'abc'}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)

    # 你可以根據實際情境補充 500 錯誤測試
    # def test_internal_error(self):
    #     ...

class AuthServiceUnitTest(TestCase):
    def test_validate_login_empty(self):
        result = AuthService.validate_login('', '')
        self.assertEqual(result, (None, 'Username and password required'))

    def test_validate_register_empty(self):
        result = AuthService.validate_register('', '')
        self.assertEqual(result, (None, 'Username and password are required'))

    def test_login_invalid_credentials(self):
        result = AuthService.login('notexist', 'wrong')
        self.assertEqual(result, (None, 'Invalid credentials'))

    def test_register_empty(self):
        result = AuthService.register('', '')
        self.assertEqual(result, (None, 'Username and password are required'))

# class TopChartsServiceUnitTest(TestCase):
#     def test_rank_change_new(self):
#         ...
