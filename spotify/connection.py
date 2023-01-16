import os.path

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import configparser

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
config_path = ROOT_DIR + '\\spotify\\configfile.ini'


def connect_spotify_from_config() -> spotipy.client.Spotify:
    conn_dict = read_config()
    return connect_spotify(**conn_dict)


def connect_spotify(client_id, secret_id, scope, uri) -> spotipy.client.Spotify:
    auth_manager = SpotifyOAuth(client_id=client_id, client_secret=secret_id, redirect_uri=uri,
                                scope=scope, requests_session=True)
    return spotipy.Spotify(auth_manager=auth_manager)


def read_config() -> dict:
    assert os.path.exists(config_path), 'config_path does not exist'
    config_obj = configparser.ConfigParser()
    config_obj.read(config_path)
    conn_dict = config_obj['connection']

    return {'client_id': conn_dict['client_id'], 'secret_id': conn_dict['secret_id'],
            'scope': conn_dict['scope'], 'uri': conn_dict['uri']}


def create_config_for_connection():
    configuration_dict = {'client_id': '...',
                          'secret_id': '...',
                          'scope': 'playlist-read-private playlist-read-private playlist-modify-private '
                                   'user-read-recently-played user-modify-playback-state',
                          'uri': 'http://127.0.0.1:9000/'}

    config = configparser.ConfigParser()
    config.add_section('connection')

    for key, value in configuration_dict.items():
        config.set('connection', key, value)

    with open(config_path, 'w') as configfile:
        config.write(configfile)

