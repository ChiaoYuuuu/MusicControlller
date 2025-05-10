# 🚀 MusicSync: Collaborative Spotify Listening Side Project

A modern, full-stack web app that lets friends gather in virtual rooms and enjoy synchronized Spotify playback—music **and** podcasts—in real time.  
Hosts control playback; guests vote to skip or rewind tracks. Plus, an Oracle-backed Top Charts feature surfaces the current Top 10 in TW, JP, KR, and US.  


## 🔥 Highlights

- **Real-time sync** of Spotify music & podcasts across multiple users  
- **Host controls**: play, pause, skip, rewind  
- **Guest voting**: democracy in action (skip / rewind)  
- **JWT-secured** login, logout, and room-access  
- **Oracle XE integration** for storing & querying global Top 10 charts  
- **Configurable dropdown** UI for regional Top 10 (TW, JP, KR, US)  
- **Docker-first**: one command to spin up backend, Oracle XE, Redis  


## 🏗 Architecture & Tech Stack

| Layer            | Technology              |  
|------------------|-------------------------|  
| Frontend         | React, Material-UI      |  
| Backend          | Django 4.2, DRF, Celery |  
| Auth             | JWT (djangorestframework-simplejwt) |  
| Data stores      | PostgreSQL (App data), Oracle XE (Charts), Redis (Celery broker & cache) |  
| Containerization | Docker, Docker Compose  |  
| Load testing     | Locust                  |  


## ⚙️ Prerequisites

- Docker & Docker Compose installed  
- Spotify Premium account (required for playback API)  
- Optional: local `docker` group membership to avoid `sudo`  


## 🛠️ Quickstart

1. **Clone & enter project**  
   ```
   git clone https://github.com/ChiaoYuuuu/MusicController.git  
   cd MusicController
   ```

2. **Copy & configure environment**
   ```
   cp .env.example .env
   ```

   **Edit .env**  
   ```
   SPOTIFY_CLIENT_ID=your_spotify_client_id  
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret  
   SPOTIFY_REDIRECT_URI=http://localhost:8000/spotify/redirect  
    
   # Oracle XE (in Docker)
   DB_ORACLE_USER=system  
   DB_ORACLE_PASSWORD=oracle123  
   DB_ORACLE_HOST=oracle-xe  
   DB_ORACLE_PORT=1521  
   DB_ORACLE_NAME=XEPDB1  
   ```

3. **Build & launch all services**
   ```
   docker-compose up -d --build
   ```
   
    - web: Django + DRF + Celery worker  
    - oracle-xe: Oracle XE 21c  
    - redis: broker & Django cache  
    - postgres: primary app database

4. **Verify**
    - API docs & health: http://localhost:8000/api/  
    - Frontend UI: http://localhost:8000/  
    - Oracle listener: localhost:1521

5. **View real-time logs**
   ```
   docker-compose logs -f web
   ```

##  🚦 Performance & Testing
  Index: Room.host indexed for ultra-fast lookups  
  Connection pooling: CONN_MAX_AGE=60 reuses DB connections  
  Load tests with Locust:  
  ```
  locust -f locustfile.py \
    --headless \
    --users 200 --spawn-rate 20 \
    --host http://localhost:8000 \
    --run-time 2m \
    --csv load_test
  ```
  Metrics tracked: Avg/Median/Percentiles/Req-per-sec/Failure Rate  

## 📌 Tips & Tricks
1. Switch off DEBUG in production (DEBUG=False, set ALLOWED_HOSTS)  
2. Use Gunicorn / Uvicorn instead of runserver for concurrency  
3. Enable Celery Beat & Celery Flower for scheduled tasks & monitoring  
4. Persist Oracle data via Docker volume (avoid docker-compose down -v)  

## 🤝 Contributing
1. Fork & clone  
2. Create feature branch  
3. Run tests & lint  
4. Open a PR with a clear description  

## 🎓 Credit
Inspired by Tech With Tim’s Music Controller tutorial — supercharged by ChiaoYuuuu with JWT auth, Oracle Charts, and production-grade Docker setup.



