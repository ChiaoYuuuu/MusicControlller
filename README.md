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

## 🛠️ Setup Instructions
1. Install backend dependencies
bash
pip install -r requirements.txt

2. Set up environment variables
Make sure to configure your .env file or Django settings with your Spotify credentials:  
env  
SPOTIFY_CLIENT_ID=your_spotify_client_id  
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret  
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8000/spotify/redirect

3. Run Django backend
bash
python manage.py runserver

4. Install frontend dependencies and compile
Navigate to your frontend/ directory and run:
bash
npm install
npm run dev
This will start the Webpack development server to watch for changes in your React frontend.

### Clone the repository
bash
git clone https://github.com/ChiaoYuuuu/MusicControlller.git  
cd MusicControlller

## 📌 Notes
You must have a Spotify Premium account for playback to work.  
Spotify authentication uses OAuth2 and is tied to each user’s Spotify account.  
Rooms are tied to Django-authenticated users, and only one room per host is allowed.  

## 📚 Credit
Originally inspired by Tech With Tim’s tutorial  
Enhancements, feature upgrades, and bug fixes by ChiaoYuuuu  
