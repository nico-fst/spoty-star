import requests
from flask import session, abort, jsonify

BASE_HEADERS = {
    "Content-Type": "application/json",
}

def spotify_get(url: str, *, add_auth: bool = True, **kwargs):
    headers = BASE_HEADERS.copy()
    if add_auth:
        access_token = session.get('access_token')
        if not access_token:
            abort(401, description="No access token in session.")
        headers["Authorization"] = f"Bearer {access_token}"
    
    resp = requests.get(url, headers=headers, **kwargs)
    if not resp.ok:
        abort(resp.status_code, description=f"Spotify API Error (gettting {url}: {resp.text}")
    
    return resp

def spotify_post(url: str, json=None, *, add_auth: bool = True, **kwargs):
    headers = BASE_HEADERS.copy()
    if add_auth:
        access_token = session.get('access_token')
        if not access_token:
            abort(401, description="No access token in session.")
        headers["Authorization"] = f"Bearer {access_token}"
        
    resp = requests.post(url, headers=headers, json=json, **kwargs)
    if not resp.ok:
        abort(resp.status_code, description=f"Spotify API Error (posting {url}): {resp.text}")
        
    return resp