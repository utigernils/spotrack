import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import current_app, session
from datetime import datetime
from app.models import Track
from app import db


def get_spotify():
    if not current_app.config['SPOTIFY_CLIENT_ID'] or not current_app.config['SPOTIFY_CLIENT_SECRET']:
        raise ValueError("Spotify credentials not properly configured")

    auth_manager = SpotifyOAuth(
        client_id=current_app.config['SPOTIFY_CLIENT_ID'],
        client_secret=current_app.config['SPOTIFY_CLIENT_SECRET'],
        redirect_uri=current_app.config['SPOTIFY_REDIRECT_URI'],
        scope='user-read-recently-played user-read-currently-playing',
        cache_handler=None  # Disable cache to prevent file permission issues
    )

    return spotipy.Spotify(auth_manager=auth_manager)


def update_listening_history():
    sp = get_spotify()
    recent_tracks = sp.current_user_recently_played(limit=50)

    if not recent_tracks or 'items' not in recent_tracks:
        return

    for item in recent_tracks['items']:
        if not item or 'track' not in item:
            continue

        track_data = item['track']
        if not track_data or 'id' not in track_data:
            continue

        track_id = track_data['id']
        track = Track.query.get(track_id)

        if not track:
            # Initialize a new track with default values
            track = Track(
                id=track_id,
                name=track_data.get('name', 'Unknown Track'),
                artist=track_data.get('artists', [{'name': 'Unknown Artist'}])[0]['name'],
                play_count=0,
                total_listen_time_ms=0
            )
            db.session.add(track)

        # Ensure play_count and total_listen_time_ms are initialized
        if track.play_count is None:
            track.play_count = 0
        if track.total_listen_time_ms is None:
            track.total_listen_time_ms = 0

        # Update track information
        track.play_count += 1
        track.total_listen_time_ms += track_data.get('duration_ms', 0)

        # Update last_listened time if available
        if 'played_at' in item:
            track.last_listened = datetime.fromisoformat(item['played_at'].replace('Z', '+00:00'))
        else:
            track.last_listened = datetime.utcnow()

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise Exception(f"Error updating listening history: {str(e)}")


def get_listening_stats():
    try:
        total_time = db.session.query(db.func.sum(Track.total_listen_time_ms)).scalar() or 0
        most_played = Track.query.order_by(Track.play_count.desc()).limit(5).all()
        recent_tracks = Track.query.order_by(Track.last_listened.desc()).limit(5).all()

        return {
            'total_time': total_time // 1000,  # Convert to seconds
            'most_played': [track.to_dict() for track in most_played],
            'recent_tracks': [track.to_dict() for track in recent_tracks]
        }
    except Exception as e:
        raise Exception(f"Error getting listening stats: {str(e)}")