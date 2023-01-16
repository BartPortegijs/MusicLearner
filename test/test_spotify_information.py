import unittest
import spotipy
import time

import spotify.information as sp_inf
import spotify.interaction as sp_int
import spotify.connection as sp_conn
from data_classes import *

from test.test_classes import TestTrack
from test.data_for_tests import track_single, track_multiple


spotify_connection = sp_conn.connect_spotify_from_config()
spotify_information = sp_inf.SpotifyInformation(spotify_connection)

unittest_playlist = Playlist(name='unit_test')
songset_test = SongSet({track_single, track_multiple})


# Test Iterators
##############################################################
class IteratorCases:
    class IteratorTesting(unittest.TestCase):
        @classmethod
        def setUpClass(cls) -> None:
            cls.iterator = sp_inf.Iterator(spotify_connection)
            cls.resulting_type = None

        def test_connection(self):
            self.assertIsInstance(self.iterator._sp_conn, spotipy.client.Spotify)

        def test_get_iterator(self):
            self.assertIsInstance(self.iterator._iterator, dict)

        def test_get_item_class(self):
            item = self.iterator.get_results()[0]
            self.assertIsInstance(item, self.resulting_type)

        def test_get_results(self):
            if self.resulting_type == Playlist:
                for item in self.iterator.get_results():
                    self.assertIsInstance(item, self.resulting_type)
            if self.resulting_type == Track:
                songset = self.iterator.get_results()
                self.assertIsInstance(songset, SongSet)

        def test_next(self):
            iter_dict = self.iterator._iterator.copy()
            if self.iterator['next']:
                next(self.iterator)
                self.test_get_iterator()
                self.assertNotEqual(iter_dict, self.iterator._iterator)


class TestPlaylistIterator(IteratorCases.IteratorTesting):
    @classmethod
    def setUpClass(cls) -> None:
        cls.iterator = sp_inf.PlaylistIterator(spotify_connection)
        cls.resulting_type = Playlist


class TestSearchTrackIterator(IteratorCases.IteratorTesting):
    @classmethod
    def setUpClass(cls) -> None:
        cls.iterator = sp_inf.SearchTrackIterator(spotify_connection, query='beatles', limit=5)
        cls.resulting_type = Track


class TestPlaylistTrackIterator(IteratorCases.IteratorTesting):
    @classmethod
    def setUpClass(cls) -> None:
        pl_interaction = sp_int.PlaylistInteraction.create_playlist(spotify_connection, unittest_playlist)
        pl_interaction.add_songset(songset_test)

        cls.iterator = sp_inf.PlaylistTrackIterator(spotify_connection, pl_interaction.playlist)
        cls.resulting_type = Track

    @classmethod
    def tearDownClass(cls):
        pl_interaction = sp_int.PlaylistInteraction(spotify_connection, unittest_playlist)
        pl_interaction.delete_playlist()


class TestPlayedTrackIterator(IteratorCases.IteratorTesting):
    @classmethod
    def setUpClass(cls) -> None:
        cls.iterator = sp_inf.PlayedTrackIterator(spotify_connection)
        cls.resulting_type = Track

    test_next = None


# Playlist tests
##############################################################
class TestPlaylistGet(unittest.TestCase):
    pl_interaction = None

    @classmethod
    def setUpClass(cls) -> None:
        sp_int.PlaylistInteraction.create_playlist(spotify_connection, unittest_playlist)

    @classmethod
    def tearDownClass(cls):
        pl_interaction = sp_int.PlaylistInteraction(spotify_connection, unittest_playlist)
        pl_interaction.delete_playlist()

    def _playlist_interaction_getter(self):
        if not self.pl_interaction:
            self.pl_interaction = sp_int.PlaylistInteraction(spotify_connection, unittest_playlist)

    def test_get_relevant_playlists(self):
        playlist_list = spotify_information.get_relevant_playlists()
        self.assertGreater(len(playlist_list), 50)

    def test_get_playlist_from_playlist(self):
        self._playlist_interaction_getter()
        playlist2 = spotify_information.get_playlist_from_playlist(unittest_playlist)
        self.assertEqual(self.pl_interaction.playlist, playlist2)

    def test_get_playlist_from_spotify_id(self):
        self._playlist_interaction_getter()
        playlist = self.pl_interaction.playlist
        playlist2 = spotify_information.get_playlist_from_spotify_id(playlist.spotify_id)
        self.assertEqual(playlist, playlist2)

    def test_get_songset_from_playlist(self):
        self._playlist_interaction_getter()
        self.pl_interaction.add_songset(songset_test)
        songset = spotify_information.get_songset_from_playlist(self.pl_interaction.playlist)
        self.assertEqual(songset, songset_test)


# Track Test
##############################################################
# class TestTrackFromSpotifyId(TestTrack):
#     @classmethod
#     def setUpClass(cls) -> None:
#         cls.track = spotify_information.get_track_from_spotify_id(spotify_id_single)


class TestSearchTracks(TestTrack):
    @classmethod
    def setUpClass(cls) -> None:
        cls.track = spotify_information.get_songset_from_search_query('Beatles yesterday', 1)[0]


# class TestLastPlayedTracks(unittest.TestCase):
#     spotify_id = track_single.spotify_id
#
#     @classmethod
#     def setUpClass(cls) -> None:
#         track = spotify_connection.track(cls.spotify_id)
#         cls.duration = track['duration_ms']
#         cls.track = spotify_information.get_track_from_spotify_id(cls.spotify_id)
#
#         spotify_connection.start_playback(uris=[f'https://open.spotify.com/track/{cls.spotify_id}'],
#                                           position_ms=cls.duration - 1)
#         time.sleep(1)
#
#     def test_get_last_played_since(self):
#         songset = spotify_information.get_last_played_tracks_since(int(time.time() - 500))
#         self.assertIn(self.track, songset)
#
#     def test_get_last_played(self):
#         songset = spotify_information.get_last_played_tracks()
#         self.assertIn(self.track, songset)


class TestGetSongsetFromPlaylist(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        sp_int.PlaylistInteraction.create_playlist(spotify_connection, unittest_playlist)

    @classmethod
    def tearDownClass(cls):
        pl_interaction = sp_int.PlaylistInteraction(spotify_connection, unittest_playlist)
        pl_interaction.delete_playlist()
