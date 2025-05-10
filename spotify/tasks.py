from celery import shared_task
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
from datetime import datetime
import oracledb
from spotipy.oauth2 import SpotifyOAuth
from .credentials import *

load_dotenv()

COUNTRY_PLAYLIST_IDS = {
    "JP": "2nSSnQqIy2pqZaDpGsw1IB",
    "TW": "792jG1h3j0Kd9dv8xekW3d",
    "KR": "1vQtY5NkVzMSKlYZsHuG1F",
    "US": "3lkcsvawcPzffVY1g0yq44",
}


@shared_task
def fetch_and_store_top10_task():
    print(f"[{datetime.now()}] 🚀 Starting Spotify Top 50 task!!!")

    playlist_link = "https://open.spotify.com/playlist/37i9dQZEVXbNG2KDcFcKOF?si=1333723a6eff4b7f"
    playlist_URI = playlist_link.split("/")[-1].split("?")[0]
    print("URI : ", playlist_URI)

    # 建立 Spotify API client
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    print("SPOTIFY ID : ", client_id, "\n Spotify PW : ", client_secret)
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

    # 建立 Oracle DB 連線
    try:
        conn = oracledb.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            dsn=DB_DSN
        )
        cursor = conn.cursor()
    except Exception as e:
        print(f"❌ Oracle connection error: {e}")
        return

    now = datetime.now()

    for country, playlist_id in COUNTRY_PLAYLIST_IDS.items():
        try:
            print(f"Fetching playlist for {country}")
            results = sp.playlist_tracks(playlist_id)
            tracks = results['items']
            while results['next']:
                results = sp.next(results)
                tracks.extend(results['items'])

            for i, item in enumerate(tracks[:10], start=1):
                track = item['track']
                if not track:
                    continue

                song_name = track['name']
                artist_name = track['artists'][0]['name'] if track['artists'] else ''
                track_id = track['id']
                spotify_url = track['external_urls']['spotify']

                cursor.execute("""
                    INSERT INTO top_charts (
                        COUNTRY_CODE, RANK, SONG_NAME, ARTIST_NAME,
                        TRACK_ID, SPOTIFY_URL, RETRIEVED_AT
                    ) VALUES (:1, :2, :3, :4, :5, :6, :7)
                """, (
                    country, i, song_name, artist_name,
                    track_id, spotify_url, now
                ))

            print(f"Stored {country} Top 10")
        except Exception as e:
            print(f"Failed to process {country}: {e}")
            continue

    conn.commit()
    cursor.close()
    conn.close()
    print("All done and committed to Oracle DB.")


if __name__ == "__main__":
    fetch_and_store_top10_task()
