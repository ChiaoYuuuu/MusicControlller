# 🚀 MusicSync

**MusicSync** 是一個用 Python（Django + DRF + Celery）與 React 編寫的全端專案，讓朋友們可以在虛擬房間同步收聽 Spotify 音樂或 Podcast。
支援房主控制播放、來賓投票跳過/回播、即時同步、排行榜查詢等功能。
適合遠端聚會、線上音樂派對、團體收聽等場景。

---

## 主要特點

- 多人即時同步 Spotify 播放
- 房主控制播放、暫停、跳過、回播
- 來賓投票跳過/回播
- JWT 安全登入、房間驗證
- 支援地區排行榜（TW, JP, KR, US）
- Docker 一鍵啟動全服務

---

## 專案技術

| 層級         | 技術                        |
|--------------|-----------------------------|
| 後端         | Django 4.2, DRF, Celery     |
| 認證         | JWT (djangorestframework-simplejwt) |
| 資料庫       | PostgreSQL, Redis           |
| 容器化       | Docker, Docker Compose      |
| 測試         | Locust, coverage            |

---

## 安裝要求

- Python 3.8+
- Docker & Docker Compose
- Spotify Premium 帳號（API 播放需用）
- Node.js（如需前端本地開發）
- PostgreSQL、Redis（Docker 會自動啟動）

### Python 依賴（`requirements.txt`）
- Django 4+
- djangorestframework
- requests
- spotipy
- celery
- psycopg2-binary
- 其他詳見 `requirements.txt`

---

## 安裝與啟動

1. **Clone 專案**
   ```bash
   git clone https://github.com/ChiaoYuuuu/MusicController.git
   cd MusicController
   ```

2. **設定環境變數**
   ```bash
   cp .env.example .env
   # 編輯 .env，填入 Spotify API 金鑰
   ```

3. **啟動服務（建議用 Docker）**
   ```bash
   docker-compose up -d --build
   ```
   - 啟動 Django + Celery + Redis + PostgreSQL

4. **前端開發（可選）**
   ```bash
   cd frontend
   npm install
   npm start
   ```

5. **驗證服務**
   - API docs: [http://localhost:8000/api/](http://localhost:8000/api/)
   - 前端 UI: [http://localhost:8000/](http://localhost:8000/)

---

## 使用概述

- 註冊/登入 → 建立房間 → 分享房間碼 → 來賓加入
- 房主可控制播放，來賓可投票跳過/回播
- 支援排行榜查詢

---

## 專案架構

```
MusicControlller/
├── api/                # Django app，API views、serializers、service、application、domain、repository
│   ├── controller/     # API views (auth, room, topcharts...)
│   ├── application/    # Application 層，調用 service 處理框架功能
│   ├── domain/         # 純商業邏輯（service）
│   ├── infrastructure/ # ORM models、serializers
│   ├── repository/     # DB 查詢封裝
│   └── ...
├── spotify/            # Spotify 整合相關（client, domain, infrastructure, controller）
│   ├── infrastructure/ # SpotifyToken, SkipVote, client, repository
│   ├── application/    # 播放控制應用層
│   └── ...
├── frontend/           # React 前端專案
│   ├── src/components/ # React 元件
│   └── ...
├── test/               # 測試（unit, integration, stress）
│   ├── unit/           # 單元測試
│   ├── integration/    # 整合測試
│   └── stress/         # 壓力測試（Locust）
├── project_root/       # Django 專案設定（settings, urls, celery, asgi, wsgi）
├── manage.py           # Django 管理指令
├── requirements.txt    # Python 依賴
├── docker-compose.yml  # Docker 組態
├── Dockerfile          # Docker 建置
└── README.md           # 專案說明
```

- **api/**：後端主 API app，分層清楚，易於維護與擴充。
- **spotify/**：Spotify OAuth、播放控制、token 管理等。
- **frontend/**：React 前端 SPA。
- **test/**：單元、整合、壓力測試。
- **project_root/**：Django 專案設定與 Celery。

---

## 測試與故障排除

- **單元測試**  
  ```bash
  coverage run --rcfile=.coveragerc manage.py test
  ```
  - 測試檔案位於 `test/unit/`，如 `test_api.py`, `test_spotify.py`
  - 若遇到 `SpotifyToken` unique constraint 問題，請先清空資料表：
    ```python
    from spotify.infrastructure.models import SpotifyToken
    SpotifyToken.objects.all().delete()
    ```
  - `SpotifyToken.user` 欄位型態為 CharField，所有 token 相關操作都必須用 user_id 的字串（如 `str(user.id)`）

- **常見問題**
  - Docker 啟動異常：請檢查 .env 設定與 port 是否被佔用
  - Spotify 播放失敗：需 Spotify Premium 帳號，且裝置需啟動 Spotify App

- **更多細節**  
  - 參見 [Django 官方文件](https://docs.djangoproject.com/zh-hans/4.2/)
  - 參見 [Spotify API 文件](https://developer.spotify.com/documentation/web-api/)

---

## 相關資源

- [Django REST framework](https://www.django-rest-framework.org/)
- [Celery](https://docs.celeryq.dev/en/stable/)
- [React](https://react.dev/)
- [Docker 官方文檔](https://docs.docker.com/)
- [本專案 GitHub](https://github.com/ChiaoYuuuu/MusicController)

---

如需更詳細的開發、測試、貢獻說明，請參閱專案內其他說明文件或直接聯絡作者。


