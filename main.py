import json
import time
import sqlite3
from datetime import datetime
from flask import Flask, jsonify, render_template
from spotipy.oauth2 import SpotifyOAuth
import spotipy
import threading

with open("config.json", "r") as config_file:
    config = json.load(config_file)

CLIENT_ID = config["CLIENT_ID"]
CLIENT_SECRET = config["CLIENT_SECRET"]
REDIRECT_URI = config["REDIRECT_URI"]
SCOPE = config["SCOPE"]

DB_NAME = "spotify_log.db"

app = Flask(__name__)

def initialize_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS listening_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def get_spotify_status(sp):
    try:
        playback = sp.current_playback()
        if playback and playback.get("is_playing"):
            return "listening"
        else:
            return "not listening"
    except Exception as e:
        print(f"Fehler beim Abrufen des Status: {e}")
        return "error"

def log_status(status):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO listening_log (timestamp, status) VALUES (?, ?)", (timestamp, status))
    conn.commit()
    conn.close()

def calculate_listening_time():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM listening_log WHERE status = 'listening'")
    listening_records = cursor.fetchall()
    conn.close()

    total_time = len(listening_records) * 20  # Jede Eintragung repräsentiert 20 Sekunden
    return total_time

def track_spotify_status():
    initialize_database()
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                                   client_secret=CLIENT_SECRET,
                                                   redirect_uri=REDIRECT_URI,
                                                   scope=SCOPE))
    while True:
        status = get_spotify_status(sp)
        log_status(status)
        print(f"Status geloggt: {status}")
        time.sleep(20)

@app.route("/")
def home():
    listening_time_seconds = calculate_listening_time()
    listening_time_minutes = listening_time_seconds // 60
    return render_template("index.html", minutes=listening_time_minutes)

@app.route("/api/listening_time", methods=["GET"])
def api_listening_time():
    listening_time_seconds = calculate_listening_time()
    listening_time_minutes = listening_time_seconds // 60
    return jsonify({"listening_time_minutes": listening_time_minutes})

def main():
    threading.Thread(target=track_spotify_status, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    main()
