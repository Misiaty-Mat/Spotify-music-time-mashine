from bs4 import BeautifulSoup
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import spotipy
import requests
import os

load_dotenv()


URL = "https://www.billboard.com/charts/hot-100/"

SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
SPOTIFY_USER_ID = os.environ.get("SPOTIFY_USER_ID")


travel_to_date = input("What date would you like to travel? (YY MM DD)\n>> ").split()
travel_to_date_formated = (
    travel_to_date[0] + "-" + travel_to_date[1] + "-" + travel_to_date[2]
)
try:
    url_destination = URL + travel_to_date_formated
except IndexError:
    print("Wrong date format")
else:
    spotify_response = requests.get(url_destination)
    spotify_response.raise_for_status()

    spotify_html_code = spotify_response.text

    songs_soup = BeautifulSoup(spotify_html_code, "html.parser")

    top_100_song_titles_to_strip = songs_soup.find_all(
        name="span",
        class_="chart-element__information__song text--truncate color--primary",
    )

    top_100_song_titles_striped = [
        song_title.get_text() for song_title in top_100_song_titles_to_strip
    ]


# Spotify API authentication
scope = "playlist-modify-private"
auth_manager = SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    scope=scope,
    redirect_uri="http://example.com",
)

spotify_api = spotipy.Spotify(auth_manager=auth_manager)

year = travel_to_date[0]

song_uris = []

for song in top_100_song_titles_striped:
    result = spotify_api.search(q=f"track:{song} year:{year}", type="track")
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")


playlist = spotify_api.user_playlist_create(
    user=SPOTIFY_USER_ID, name=f"{travel_to_date_formated} bilboard 100", public=False
)

playlist_id = playlist["id"]

spotify_api.user_playlist_add_tracks(
    SPOTIFY_USER_ID, playlist_id, song_uris, position=None
)
