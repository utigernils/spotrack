from app import create_app

app = create_app()

if __name__ == '__main__':
    try:
        print("Starting server on port 5000")
        print(f"Redirect URI: {app.config['SPOTIFY_REDIRECT_URI']}")
        app.run(debug=True, port=5000)
    except Exception as e:
        print(f"Error starting server: {str(e)}")