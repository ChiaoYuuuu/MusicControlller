from rest_framework.test import APITestCase
import uuid

class FullIntegrationFlowTest(APITestCase):
    def setUp(self):
        self.username = f"integration_{uuid.uuid4().hex[:8]}"
        self.password = "testpass"
        # 註冊
        reg_resp = self.client.post('/api/register', {'username': self.username, 'password': self.password}, format='json')
        self.assertIn(reg_resp.status_code, [200, 201])
        # 登入
        login_resp = self.client.post('/api/login', {'username': self.username, 'password': self.password}, format='json')
        self.assertEqual(login_resp.status_code, 200)
        self.access_token = login_resp.data['access']
        self.auth_header = {'HTTP_AUTHORIZATION': f'Bearer {self.access_token}'}

    def test_full_user_room_spotify_flow(self):
        # 建立房間
        create_resp = self.client.post('/api/create-room', {'guest_can_pause': True, 'votes_to_skip': 2}, format='json', **self.auth_header)
        self.assertIn(create_resp.status_code, [200, 201])
        room_code = create_resp.data['code']

        # 取得房間資訊
        get_room_resp = self.client.get(f'/api/get-room?code={room_code}', **self.auth_header)
        self.assertEqual(get_room_resp.status_code, 200)
        self.assertEqual(get_room_resp.data['code'], room_code)

        # 加入房間
        join_resp = self.client.post('/api/join-room', {'code': room_code}, format='json', **self.auth_header)
        self.assertEqual(join_resp.status_code, 200)

        # 查詢 Spotify 認證 URL
        auth_url_resp = self.client.get('/spotify/get-auth-url', **self.auth_header)
        self.assertEqual(auth_url_resp.status_code, 200)
        self.assertIn('url', auth_url_resp.data)

        # 查詢排行榜
        top_song_resp = self.client.get('/api/top-song')
        self.assertEqual(top_song_resp.status_code, 200)
        self.assertIn('TW', top_song_resp.data)

        # 投票 skip song（流程測試，不驗證 Spotify token）
        skip_resp = self.client.post('/spotify/skip', {'room_code': room_code}, format='json', **self.auth_header)
        self.assertIn(skip_resp.status_code, [200, 204, 400, 404])

        # 離開房間
        leave_resp = self.client.post('/api/leave-room', {'room_code': room_code}, format='json', **self.auth_header)
        self.assertEqual(leave_resp.status_code, 200) 