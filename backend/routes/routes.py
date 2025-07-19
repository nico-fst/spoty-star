from flask import Blueprint
from .auth_routes import auth_bp
from .playlist_routes import playlist_bp
from .test_routes import test_bp
from .playlists_get_routes import playlists_get_bp

api_bp = Blueprint('api', __name__)

api_bp.register_blueprint(auth_bp)
api_bp.register_blueprint(playlist_bp)
api_bp.register_blueprint(test_bp)
api_bp.register_blueprint(playlists_get_bp)