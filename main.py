from flask import Flask, redirect, request, session, url_for
import requests
import base64
import json
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URL = 'http://localhost:5001/callback'
AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
SCOPE = 'user-read-playback-state user-read-currently-playing'

@app.route('/')
def index():
    return 'Hello, melde dich an unter <a href="/login">Login</a>'

@app.route('/login')
def login():
    # login optional, debug: dass jedes Mal Anmeldung abgefragt
    auth_url = f"{AUTH_URL}?response_type=code&client_id={CLIENT_ID}&scope={SCOPE}&redirect_uri={REDIRECT_URL}&prompt=login"
    return redirect(auth_url)

@app.route('/callback')
def callback():
    # args werden von Spotify an die URL /callback angehangen
    code = request.args.get('code')
    
    if not code:
        return 'Fehler beim Login: Kein Authorizaton Code erhalten'
    
    # Exchange Authorization Code -> Access token
    token_resp = requests.post(TOKEN_URL, data={
        'grant_type': "authorization_code",
        'code': code,
        'redirect_uri': REDIRECT_URL,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    })
    
    # Response with Token
    token_info = token_resp.json()
    session['access_token'] = token_info['access_token']
    
    return redirect(url_for('currently_playing'))

@app.route('/currently_playing')
def currently_playing():
    token = session['access_token']
    
    if not token:
        return redirect(url_for('login'))
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    # -> resp.json()['item'] liefert album, artists, duration, ...
    resp = requests.get('https://api.spotify.com/v1/me/player/currently-playing', headers=headers)
    
    if resp.status_code == 200 and resp.json():
        track_data = resp.json()
        
        track_name = track_data['item']['name']
        track_artist_name = track_data['item']['artists'][0]['name']
        track_year = track_data['item']['album']['release_date'].split('-')[0]
        
        return f'Aktuell läuft: {track_name} von {track_artist_name}, veröffentlicht im Jahr {track_year}'
    else:
        return 'Kein Song läuft gerade'
    


if __name__ == '__main__':
    app.run(host="localhost", port=5001, debug=True)