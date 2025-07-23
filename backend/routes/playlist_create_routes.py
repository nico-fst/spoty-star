from flask import Blueprint, session, jsonify
from typing import Dict, TypedDict, List
import requests
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from ..app_types import Playlist
from ..utils import token_required
from ..utils_requests import spotify_get, spotify_post
from ..thread_context import set_access_token, get_access_token
from .playlists_get_routes import get_playlists
from ..utils_playlists import get_user_id

playlist_create_bp = Blueprint('playlist_create_bp', __name__)


@playlist_create_bp.route('/api/create_monthlist/<year>/<month>')
@token_required
def create_monthlist(year: str, month: str) -> Playlist:
    selected_date = datetime(int(year), int(month), 1)
    now = datetime.now()
    
    if selected_date > now:
        return jsonify({"error": "Cannot create playlist for future dates."}), 401

    title = f"[Time] {year}::{month.zfill(2)}"
    playlists = get_playlists()
    
    if any(pl['name'] == title for pl in playlists):
        return jsonify({"message": f"Playlist '{title}' already exists."}), 400
    
    user_id = get_user_id()
    try:
        resp = spotify_post(f"https://api.spotify.com/v1/users/{user_id}/playlists", {
            "name": title
        })
    except requests.HTTPError as e:
        return jsonify({"error": str(e)}), 500
    
    return resp.json(), 201

@playlist_create_bp.route('/api/does_monthlist_exist/<playlist_name>')
@token_required
def does_monthlist_exist(playlist_name: str) -> bool:
    title = f"[Time] {playlist_name[0:4]}::{playlist_name[5:7]}"
    playlists = get_playlists()
    
    exists: bool = any(pl['name'] == title for pl in playlists)
    print(f"{title} does exist: {exists}")
    return jsonify(exists)