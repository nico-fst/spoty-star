import os
from flask import Flask, redirect, request, session, url_for, jsonify, make_response
from functools import wraps

IS_DEV = os.getenv('IS_DEV', 'false').lower() == 'true'

def ensure_domain(url: str) -> str:
    print(IS_DEV, url)
    if IS_DEV and url:
        return f"http://localhost:5173{url}"
    return url

def token_required(f):
    @wraps(f)
    def decorated_f(*args, **kwargs):
        if not 'access_token' in session:
            if request.path.startswith('/api/'):
                return make_response(jsonify({"error": "Not logged in"}), 401)
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_f