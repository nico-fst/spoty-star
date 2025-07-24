from flask import Flask, redirect, request, session, url_for, jsonify, make_response
from flask import Blueprint
import os
import requests

from ..utils import ensure_domain

from dotenv import load_dotenv

load_dotenv()

auth_bp = Blueprint("auth", __name__)

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

REDIRECT_URL = "http://localhost:5001/api/callback"
AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
SCOPE = "playlist-modify-public playlist-modify-private user-library-read user-read-playback-state user-read-currently-playing playlist-modify-public playlist-modify-private"


@auth_bp.route("/api/login")
def login():
    session["next_url"] = (
        request.args.get("next") or "/"
    )  # remember for redirecting after callback

    # login optional, debug: dass jedes Mal Anmeldung abgefragt
    auth_url = f"{AUTH_URL}?response_type=code&client_id={CLIENT_ID}&scope={SCOPE}&redirect_uri={REDIRECT_URL}&prompt=login"
    return redirect(auth_url)


@auth_bp.route("/api/logout")
def logout():
    """pseudo logout, deletes access_token from session"""
    session.pop("access_token", None)
    return redirect(url_for("index"))


@auth_bp.route("/api/loggedin")
def loggedin():
    if "access_token" in session:
        return {"success": True}, 200
    return {"success": False}, 400


@auth_bp.route("/api/callback")
def callback():
    # args werden von Spotify an die URL /callback angehangen
    code = request.args.get("code")

    if not code:
        return "Fehler beim Login: Kein Authorizaton Code erhalten"

    # Exchange Authorization Code -> Access token
    token_resp = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URL,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
    )

    # Response with Token
    token_info = token_resp.json()
    session["access_token"] = token_info["access_token"]

    print(f"Redirecting to {ensure_domain(session.get('next_url'))}")
    return redirect(ensure_domain(session.pop("next_url", url_for("index"))))
