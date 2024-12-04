from flask import Blueprint, jsonify, redirect, url_for, current_app, request
from app.spotify_client import get_spotify, update_listening_history, get_listening_stats
from spotipy.oauth2 import SpotifyOAuth

main = Blueprint('main', __name__)

@main.route('/')
def index():
    try:
        if not current_app.config['SPOTIFY_CLIENT_ID'] or not current_app.config['SPOTIFY_CLIENT_SECRET']:
            return "Please set up your Spotify credentials in .env file", 400
            
        sp = get_spotify()
        auth_manager = sp.auth_manager
        if not auth_manager.validate_token(auth_manager.cache_handler.get_cached_token()):
            auth_url = auth_manager.get_authorize_url()
            return redirect(auth_url)
        return redirect(url_for('main.stats'))
    except Exception as e:
        return f"Error: {str(e)}", 500

@main.route('/callback')
def callback():
    try:
        sp = get_spotify()
        token = sp.auth_manager.get_access_token(request.args.get('code'))
        return redirect(url_for('main.stats'))
    except Exception as e:
        return f"Error during callback: {str(e)}", 500

@main.route('/stats')
def stats():
    try:
        update_listening_history()
        return jsonify(get_listening_stats())
    except Exception as e:
        return jsonify({"error": str(e)}), 500