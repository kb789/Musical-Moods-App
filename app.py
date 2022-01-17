from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import requests
from requests.auth import HTTPBasicAuth
import os


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    cors = CORS(app,
                resources={r"/*": {"origins": "*"}},
                supports_credentials=True)

    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type, Authorization')
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET, DELETE, POST')
        return response

    def get_auth():
        """
        Gets access token needed to use the Spotify API.
        """
        url = "https://accounts.spotify.com/api/token"
        client_id = os.environ['client_id']
        client_secret = os.environ['client_secret']
        body = {"grant_type": "client_credentials"}
        r = requests.post(url, auth=HTTPBasicAuth(client_id, client_secret), data=body)
        response = r.json()
        return (
            response["access_token"]
        )

    @app.route('/searchSong', methods=['GET', 'POST'])
    def search_song():
        """
        Gets song_id, album and album image for a song from Spotify API
        """
        search_term = request.json.get("songname")
        search_term2 = request.json.get("artist")
        search_string = "artist" + ":" + search_term2 + " " + "track" + ":" + search_term
        url = 'https://api.spotify.com/v1/search'
        access_token = get_auth()
        headers = {'Authorization': 'Bearer ' + access_token}
        params = {
            'query': search_string,
            'type': 'track',
            'limit': 1}
        try:
            r = requests.get(url, headers=headers, params=params)
            response = r.json()
            song_id = response["tracks"]["items"][0]["id"]
            album = response["tracks"]["items"][0]["album"]["name"]
            image = response["tracks"]["items"][0]["album"]["images"][1]["url"]
            valence = track_info(song_id)
            return jsonify({
                'success': True,
                'songname': search_term,
                'response': r.json(),
                'valence': valence,
                'album': album,
                'image': image
            })
        except BaseException:
            abort(422)

    def track_info(song_id):
        """
        Gets the valence value of a song from Spotify API
        """
        url = 'https://api.spotify.com/v1/audio-features/' + song_id
        access_token = get_auth()
        headers = {'Authorization': 'Bearer ' + access_token}
        r = requests.get(url, headers=headers)
        response = r.json()
        valence = response["valence"]
        return (
            valence
        )

    @app.route('/')
    def index():
        return "<h1>Welcome to our server !!!</h1>"

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
