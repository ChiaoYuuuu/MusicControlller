# 🎵 Spotify Group Listening App
A web application that allows users in the same virtual room to synchronously listen to Spotify content—including music and podcasts—with friends.  
Users can vote to skip to the next or previous track, and the host can control playback in real-time.  
This project is based on Tech With Tim's Music Controller Web App Tutorial, with several enhancements to support modern Spotify features and user authentication.

## 🚀 Features
- ✅ Create and join rooms via room code
- ✅ Synchronized playback for **Spotify music**  
- ✅ **Synchronized playback for Spotify podcasts** *(new)*
- ✅ Host playback control and guest voting
- ✅ Vote to skip to the next track
- ✅ **Vote to go back to the previous track** *(new)*  
- ✅ **JWT-based login and logout system** *(new)*
- ✅ **Oracle database integration for storing Spotify charts** *(new)*
- ✅ **Top 10 songs display by country (TW, JP, KR, US)** *(new)*

## 📊 Top Charts UI
The homepage now includes a new feature for viewing Top 10 Spotify songs per region using dropdown selection.

<img width="330" alt="image" src="https://github.com/user-attachments/assets/16e81e94-87ab-42e4-809c-1b463c352757" />

- Countries supported: TW, JP, KR, US
- Data is fetched from Oracle database and displayed dynamically
- Dropdown allows user to switch country
- Songs shown in scrollable card with responsive layout

## 🛠️ Setup Instructions

### 1. Clone the repository
git clone https://github.com/ChiaoYuuuu/MusicControlller.git  
cd MusicControlller

### 2. Install backend dependencies
pip install -r requirements.txt

### 3. Set up environment variables
Create a .env file and fill in the following:

SPOTIFY_CLIENT_ID=your_spotify_client_id  
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret  
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8000/spotify/redirect

DB_USER=your_oracle_user
DB_PASSWORD=your_oracle_password
DB_DSN=your_oracle_dsn

### 4. Run Django backend
python manage.py makemigrations   
python manage.py migrate   
python manage.py runserver   

### 5. Install frontend dependencies and start development server
Navigate to the frontend/ directory:

npm install  
npm run dev

## 📌 Notes
You must have a Spotify Premium account for playback to work
Spotify authentication uses OAuth2
Each user can create one room only
Oracle DB must be running locally or via Docker for Top 10 feature

## 📚 Credit
Originally inspired by Tech With Tim’s tutorial
Enhancements, feature upgrades, and bug fixes by ChiaoYuuuu



