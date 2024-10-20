import openai
import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()

# Load your OpenAI API key and Spotify credentials from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_SEARCH_URL = "https://api.spotify.com/v1/search"

def get_spotify_access_token():
    # Get access token from Spotify
    response = requests.post(
        SPOTIFY_TOKEN_URL,
        data={
            'grant_type': 'client_credentials',
            'client_id': SPOTIFY_CLIENT_ID,
            'client_secret': SPOTIFY_CLIENT_SECRET,
        }
    )
    return response.json().get('access_token')

def get_songs_from_openai(prompt):
    response = openai.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",  # or any other model

        #fix/add response_format as input for chatgpt
        messages=[
            {"role": "system", "content": "You response without any addtional text and in the json format. The attributes are 'Title' and 'Artist'."},
            {"role": "user", "content": prompt}
        ]
    )
    songs_json = response.choices[0].message.content.strip('`').strip()

    if songs_json.startswith('json'):
        songs_json = songs_json[4:].strip()

    try:
        songs = json.loads(songs_json)
    except json.JSONDecodeError:
        print("Error decoding JSON: ", songs_json)
        return []
    return songs

def search_songs_on_spotify(songs, access_token):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    song_info = []

    for song in songs:

        title = song.get('Title')
        artist = song.get('Artist')

        query = f"{title} artist:{artist}"

        response = requests.get(
            SPOTIFY_SEARCH_URL,
            headers=headers,
            params={'q': query, 'type': 'track'}
        )
        
        # If there's a valid response, append the first track found
        if response.status_code == 200 and response.json()['tracks']['items']:
            track = response.json()['tracks']['items'][0]
            song_info.append({
                'name': track['name'],
                'artist': ', '.join(artist['name'] for artist in track['artists']),
                'url': track['external_urls']['spotify']
            })
        else:
            print(f"Error or no results for song: {title} by {artist}")

    return song_info

def main():
    # Example prompt
    mood_prompt = "Generate a list of songs that are uplifting and energetic."
    #mood_prompt = "sad"
    # Get song titles from OpenAI
    songs = get_songs_from_openai(mood_prompt)
    print("Songs suggested by OpenAI:", songs)
    
    # Get Spotify access token
    #access_token = get_spotify_access_token()
    
    # Search for songs on Spotify
    #song_info = search_songs_on_spotify(songs, access_token)

    # Print song information
    #for song in song_info:
        #print(f"{song['name']} by {song['artist']} - {song['url']}")

if __name__ == "__main__":
    main()
