import unittest

from spotify import interaction as sp_int
from spotify import connection as sp_conn
from spotify.information import SpotifyInformation

from data_classes import *
from test.data_for_tests import track_single, track_multiple, playlist_name, playlist_spotify_id


spotify_connection = sp_conn.connect_spotify_from_config()
sp_inf = SpotifyInformation(spotify_connection)
name = 'unit_test'


class TestUpdatePlaylistId(unittest.TestCase):
    def test_add_update(self):
        playlist = Playlist(name=playlist_name)
        pl_int = sp_int.PlaylistInteraction(spotify_connection, playlist)
        self.assertEqual(pl_int.playlist.spotify_id, playlist_spotify_id)


class TestCreatePlaylist(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pl_int = sp_int.PlaylistInteraction(spotify_connection, Playlist(name=name))
        if pl_int.playlist.spotify_id is not None:
            pl_int.delete_playlist()

    def testCreation(self):
        playlist = Playlist(name)
        self.pl_int = sp_int.PlaylistInteraction.create_playlist(spotify_connection, playlist)
        self.assertIsInstance(self.pl_int.playlist, Playlist)

    @classmethod
    def tearDownClass(cls) -> None:
        pl_int = sp_int.PlaylistInteraction(spotify_connection, Playlist(name=name))
        pl_int.delete_playlist()


class Interaction:
    class PlaylistInteraction(unittest.TestCase):
        songset_all = SongSet({track_single, track_multiple})

        def setUp(self) -> None:
            playlist = Playlist(name)
            self.playlist_interaction = sp_int.PlaylistInteraction.create_playlist(spotify_connection, playlist)
            self._add_songs()

        def _add_songs(self):
            pass

        def _get_songset(self):
            return sp_inf.get_songset_from_playlist(self.playlist_interaction.playlist)

        def tearDown(self) -> None:
            self.playlist_interaction.delete_playlist()


class TestRemovePlaylist(Interaction.PlaylistInteraction):
    def testRemovePlaylist(self):
        self.playlist_interaction.delete_playlist()
        playlist = sp_inf.get_playlist_from_playlist(Playlist(name=name))
        self.assertIsNone(playlist.spotify_id)

    def tearDown(self):
        pass


class TestAddSongs(Interaction.PlaylistInteraction):
    def testAddSongSet(self):
        self.playlist_interaction.add_songset(self.songset_all)
        songset = self._get_songset()
        self.assertEqual(self.songset_all, songset)


class TestRemoveSongs(Interaction.PlaylistInteraction):
    songset_none = SongSet(set())

    def _add_songs(self):
        self.playlist_interaction.add_songset(self.songset_all)

    def testRemoveSongSet(self):
        self.playlist_interaction.remove_songset(self.songset_all)
        songset = self._get_songset()
        self.assertEqual(self.songset_none, songset)

    def testClearPlaylist(self):
        self.playlist_interaction.clear_playlist()
        songset = self._get_songset()
        self.assertEqual(self.songset_none, songset)
