import unittest
import spotify.connection as connect
import spotipy


class TestConnection(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config_dict = connect.read_config()

    def testKeysReadConfig(self):
        parameters = {conf_parameter for conf_parameter in self.config_dict}
        parameters_expected = {'client_id', 'secret_id', 'scope', 'uri'}
        self.assertSetEqual(parameters, parameters_expected)

    def testSpotifyConnection(self):
        spotify_client = connect.connect_spotify_from_config()
        self.assertIsInstance(spotify_client, spotipy.client.Spotify)
