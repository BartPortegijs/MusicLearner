import unittest
import copy
import os

from data_classes import *
import test.data_for_tests as data
from config import playlist_configs
from database import connection as db_conn


class TestTrack(unittest.TestCase):
    """"Played_at and context are currently not tested."""
    track_dict = data.track_dict_single

    artist = data.artist_single
    artist_tuple = data.artist_tuple_single
    title = data.title_single
    spotify_id = data.spotify_id_single

    @classmethod
    def setUpClass(cls) -> None:
        cls.track = Track.from_spotify_track_dict(cls.track_dict)

    def testTrackType(self):
        """Basically tests the from_spotify_track_dict function"""
        self.assertIsInstance(self.track, Track)

    def testGetArtists(self):
        self.assertEqual(self.artist, self.track.artist)

    def testGetArtistsType(self):
        self.assertIsInstance(self.track.artist, str)

    def testGetArtistTuple(self):
        self.assertTupleEqual(self.artist_tuple, self.track.artist_tuple)

    def testGetArtistTupleType(self):
        self.assertIsInstance(self.track.artist_tuple, tuple)

    def testGetTitle(self):
        self.assertEqual(self.title, self.track.title)

    def testGetTitleType(self):
        self.assertIsInstance(self.track.title, str)

    def testGetSpotifyId(self):
        self.assertEqual(self.spotify_id, self.track.spotify_id)

    def testGetSpotifyIdType(self):
        self.assertIsInstance(self.track.spotify_id, str)


class TestTrackMultipleArtists(TestTrack):
    track_dict = data.track_dict_multiple

    artist = data.artist_multiple
    artist_tuple = data.artist_tuple_multiple
    title = data.title_multiple
    spotify_id = data.spotify_id_multiple


class TestSongset(unittest.TestCase):
    def testGetItem(self):
        for i in range(20):
            self.assertNotEqual(data.songset_all[0], data.songset_all[1])

    def testLength(self):
        self.assertEqual(len(data.songset_all), 2)

    def testContains(self):
        contain_bool = data.track_multiple in data.songset_all
        self.assertTrue(contain_bool)

    def testNotContains(self):
        contain_bool = data.track_single in data.songset_multiple
        self.assertFalse(contain_bool)

    def testSub(self):
        songset_result = data.songset_all - data.songset_multiple
        self.assertEqual(data.songset_single, songset_result)

    def testGetTrackIds(self):
        self.assertEqual(sorted(data.songset_all.get_track_ids()),
                         sorted([data.spotify_id_multiple, data.spotify_id_single]))

    def testExtend(self):
        s1 = copy.deepcopy(data.songset_multiple)
        s1.extend(data.songset_single)
        self.assertEqual(s1, data.songset_all)

    def testSample(self):
        songset_sampled = data.songset_all.sample(1)
        self.assertIsInstance(songset_sampled, SongSet)
        self.assertEqual(len(songset_sampled), 1)

    def testSampleTooHigh(self):
        songset_sampled = data.songset_all.sample(3)
        self.assertEqual(songset_sampled, data.songset_all)


class TestLearningState(unittest.TestCase):
    """Everything is tested in the database. Nothing to do here."""


class TestPlaylist(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.playlist = Playlist.from_spotify_playlist_dict(data.playlist_dict['items'][0])

    def testPlaylistType(self):
        """Basically tests the from_spotify_playlist_dict function"""
        self.assertIsInstance(self.playlist, Playlist)

    def testGetSpotifyId(self):
        self.assertEqual(data.playlist_spotify_id, self.playlist.spotify_id)

    def testGetName(self):
        self.assertEqual(data.playlist_name, self.playlist.name)


filter1 = ConfigRule(config_type='filter', variable='activity', sign='=', value='learn')
filter2 = ConfigRule(config_type='filter', variable='phase', sign='>', value=1)
max_nr_of_tracks = ConfigRule(config_type='max_nr_of_tracks', value=25)
remove_when_zero = ConfigRule(config_type='remove_when_zero', value=True)
only_update_triggered = ConfigRule(config_type='only_update_triggered', value=True)
introduction_state = ConfigRule(config_type='introduction_state', value=0)
introduction_tag = ConfigRule(config_type='introduction_tag', value='test')
remove = ConfigRule(config_type='remove', value=True)
repeat = ConfigRule(config_type='repeat', value=True)
keep_unknown = ConfigRule(config_type='keep_unknown', value=True)


class TestPlaylistConfig(unittest.TestCase):
    rule_list1 = [filter1, filter2, max_nr_of_tracks, remove_when_zero, only_update_triggered, keep_unknown]
    pl_conf1 = PlaylistConfig(playlist=Playlist(name='learn'), rules=rule_list1)

    rule_list2 = [introduction_state, introduction_tag]
    pl_conf2 = PlaylistConfig(playlist=Playlist(name='learn'), rules=rule_list2)

    rule_list3 = [remove]
    pl_conf3 = PlaylistConfig(playlist=Playlist(name='learn'), rules=rule_list3)

    rule_list4 = [repeat]
    pl_conf4 = PlaylistConfig(playlist=Playlist(name='learn'), rules=rule_list4)

    def testFilters(self):
        self.assertEqual(self.pl_conf1.filters, [filter1, filter2])

    def testMaxNrOfTracks(self):
        self.assertEqual(self.pl_conf1.max_nr_of_tracks, 25)

    def testRemoveWhenZero(self):
        self.assertEqual(self.pl_conf1.remove_when_zero, True)

    def testOnlyUpdateTriggered(self):
        self.assertEqual(self.pl_conf1.only_update_triggered, True)

    def testIntroductionState(self):
        self.assertEqual(self.pl_conf2.introduction_state, 0)

    def testIntroductionTag(self):
        self.assertEqual(self.pl_conf2.introduction_tag, 'test')

    def testRemove(self):
        self.assertEqual(self.pl_conf3.remove, True)

    def testRepeat(self):
        self.assertEqual(self.pl_conf4.repeat, True)

    def testKeepUnknown(self):
        self.assertEqual(self.pl_conf1.keep_unknown, True)

    def testPlaylist(self):
        self.assertIsInstance(self.pl_conf1.playlist, Playlist)

    def testName(self):
        self.assertEqual(self.pl_conf1.name, 'learn')

    # def testUnwantedCombination1(self):
    #     self.assertRaises(PlaylistConfig(playlist=Playlist(name='learn'),
    #                    rules=[filter1, remove]))
    #
    # def testUnwantedCombination2(self):
    #     PlaylistConfig(playlist=Playlist(name='learn'),
    #                    rules=[filter1, repeat])
    #
    # def testUnwantedCombination3(self):
    #     PlaylistConfig(playlist=Playlist(name='learn'),
    #                    rules=[introduction_state, remove])
    #
    # def testUnwantedCombination4(self):
    #     PlaylistConfig(playlist=Playlist(name='learn'),
    #                    rules=[introduction_state, repeat])

    def testAllQueries(self):
        with db_conn.DatabaseConnection('test.db') as (curs, conn):

            for config in playlist_configs:
                if config.filters is not None:
                    query, insert_values = config.create_filter_select_query()
                    curs.execute(query, insert_values)

    @classmethod
    def tearDownClass(cls) -> None:
        os.remove('test.db')
