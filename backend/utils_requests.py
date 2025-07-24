import requests
from flask import session, abort
import time

from .thread_context import get_access_token
from .exceptions import LoggedOutError, SpotifyAPIError

BASE_HEADERS = {
    "Content-Type": "application/json",
}


def spotify_get(url: str, *, add_auth: bool = True, **kwargs):
    headers = BASE_HEADERS.copy()
    if add_auth:
        access_token = get_access_token()  # in thread
        if not access_token:  # not in thread
            access_token = session.get("access_token")
        if not access_token:  # missing in session
            raise LoggedOutError()
        headers["Authorization"] = f"Bearer {access_token}"

    start = time.time()
    resp = requests.get(url, headers=headers, **kwargs)
    duration = time.time() - start
    print(f"📥 GET {url} took {duration:.2f}s")

    if not resp.ok:
        raise SpotifyAPIError(
            f"Spotify API Error (GET {url} -> {resp.status_code}): {resp.text}",
            status_code=resp.status_code,
        )

    return resp


def spotify_post(url: str, json=None, *, add_auth: bool = True, **kwargs):
    headers = BASE_HEADERS.copy()
    if add_auth:
        access_token = get_access_token()  # in thread
        if not access_token:  # not in thread
            access_token = session.get("access_token")
        if not access_token:  # missing in session
            raise LoggedOutError()
        headers["Authorization"] = f"Bearer {access_token}"

    start = time.time()
    resp = requests.post(url, headers=headers, json=json, **kwargs)
    duration = time.time() - start
    print(f"📤 POST {url} took {duration:.2f}s")

    if not resp.ok:
        raise SpotifyAPIError(
            f"Spotify API Error (POST {url} -> {resp.status_code}): {resp.text}",
            status_code=resp.status_code,
        )

    return resp
