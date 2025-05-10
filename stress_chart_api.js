import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  vus: 100,
  duration: '30s',
};

export default function () {
  let res = http.get('http://127.0.0.1:8000/api/top-song?country=TW');
  check(res, { 'status was 200': (r) => r.status === 200 });
  sleep(1);
}


// k6 - 建立房間 API 測試
// 儲存為 stress_create_room.js
import http from 'k6/http';
import { sleep } from 'k6';

export let options = {
  vus: 50,
  duration: '20s',
};

const token = 'your_jwt_token_here'; // 預設登入用戶 JWT
const headers = {
  headers: {
    Authorization: `Bearer ${token}`,
    'Content-Type': 'application/json',
  },
};

export default function () {
  http.post(
    'http://127.0.0.1:8000/api/create-room',
    JSON.stringify({
      guest_can_pause: true,
      votes_to_skip: Math.floor(Math.random() * 5) + 1,
    }),
    headers
  );
  sleep(1);
}