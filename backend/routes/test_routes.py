from flask import Blueprint, session, jsonify
import time
from concurrent.futures import ThreadPoolExecutor
import requests

from ..utils import token_required
from .playlist_routes import sort_playlist_into_decades
from ..utils_requests import spotify_get
from ..thread_context import get_access_token
from ..app_constants import MAX_THREADS

test_bp = Blueprint('test', __name__)

@test_bp.route('/api/test')
@token_required
def test():
    # # test adding tracks to playlist
    # return add_tracks_to_playlist(
    #     "[Aera] 21th::20s",
    #     [
    #         # "spotify:track:7lEptt4wbM0yJTvSG5EBof",
    #         "spotify:track:6rqhFgbbKwnb9MLmUQDhG6",  # Speak to Me, 1970, Pink Floyd
    #     ],
    # )

    # # test splitting playlist into decades
    # return split_playlist_into_decades("debug")

    # # test getting playlist with weird symbols
    # return get_playlist("[Aera] 21th::20s")

    # test sorting playlist into decades
    # return split_playlist_into_decades("debug")
    return sort_playlist_into_decades("[Time] 2022::08")

    # return str(
    #     subtract_uris_existing_in_playlist(
    #         "[Aera] 21th::20s", ["spotify:track:6rqhFgbbKwnb9MLmUQDhG6"]
    #     )
    # )

@test_bp.route('/api/reaching_test')
def reaching_test():
    return "Success!"
    
@test_bp.route('/api/reaching_test_with_token')
@token_required
def reaching_test_with_token():
    return "Success!"

@test_bp.route('/api/ai')
@token_required
def ai():
    resp = spotify_get("https://api.spotify.com/v1/audio-features/11dFghVXANMlKmJXsNCbNl")
    return resp.json() # returns only 403 since 

def fetch_favs(limit: int, offset: int, access_token: str):
    resp = requests.get(
        f"https://api.spotify.com/v1/me/playlists?limit={limit}&offset={offset}",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    try:
        return resp.json()['items']
    except (KeyError, ValueError) as e:
        print(f"⚠️ Fehler bei offset {offset}: {resp.status_code} → {resp.text}")
        return []

@test_bp.route('/api/threads')
@token_required
def threads():
    print("Starting tests...")
    
    start_iter = time.time()
    
    favs = []
    offset = 0
    limit = 50
    
    while True:
        resp = spotify_get(f"https://api.spotify.com/v1/me/tracks?limit={limit}&offset={offset}")
        songs = resp.json()['items']
        favs += songs
        
        if resp.json()['next'] is None:
            break
        offset += 50
    
    duration_iter = time.time() - start_iter
    print(f"{len(favs)} Songs iterativ gefetched in {duration_iter:.2f} seconds")
    
    # with Threads
    
    start_parallel = time.time()
    
    tracks_total = spotify_get("https://api.spotify.com/v1/me/tracks?limit=1").json()['total']
    offsets = list(range(0, tracks_total, limit))
    
    access_token = session.get('access_token') # wei in f nicht bekannt
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        favs_list_list = list(
            executor.map(
                lambda offset: fetch_favs(limit, offset, access_token), # function
                offsets # iterable
            )
        )
        
    favs_parallel = [song for result in favs_list_list for song in result]  # weil List[List[songs]]
    
    duration_parallel = time.time() - start_parallel
    print(f"{len(favs)} Songs parallel gefetched in {duration_parallel:.2f} seconds")

    return {
        "iterativ_count": len(favs),
        "parallel_count": len(favs_parallel),
        "iterativ_time": round(duration_iter, 2),
        "parallel_time": round(duration_parallel, 2),
    }

@test_bp.route('/api/token')
@token_required
def token():
    return jsonify({"token": session.get('access_token')})