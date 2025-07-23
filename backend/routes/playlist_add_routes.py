from flask import Blueprint, session, jsonify
from typing import Dict, TypedDict, List
import requests
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from ..app_types import Playlist, FavEntry, Track
from ..utils import token_required
from ..utils_requests import spotify_get, spotify_post
from ..thread_context import set_access_token, get_access_token
from .playlist_get_routes import get_playlists
from ..utils_playlists import get_user_id
from .favs_routes import get_favs
from ..utils import str_to_datetime, get_end_of_month

playlist_add_bp = Blueprint("playlist_add_bp", __name__)


def add_tracks_to_playlist(playlist: Playlist, tracks: List[Track]):
    playlist_id = playlist["id"]
    track_uris = [track["uri"] for track in tracks]

    return spotify_post(
        f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks", track_uris
    )
