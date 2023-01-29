import os
import sqlite3
import unittest
import util

from database.connection import DatabaseConnection
from database.information import DatabaseInformation
from database.interaction import DatabaseInteraction
from spotify.information import SpotifyInformation
from spotify.connection import connect_spotify_from_config

from data_classes import *
from config import learning_states, playlist_configs
import test.data_for_tests as data


class TestDatabaseInserts(unittest.TestCase):
    db_file = 'test_insert.db'
    db_conn = DatabaseConnection(db_file)
    db_inf = DatabaseInformation(db_conn.curs)
    db_int = DatabaseInteraction(db_conn.curs, db_conn.conn)

    @classmethod
    def tearDownClass(cls) -> None:
        """Delete database"""
        del cls.db_inf
        del cls.db_int
        del cls.db_conn
        os.remove(cls.db_file)

    def _format_correct_insert_test(self, insert_func, test_table, expected_result):
        insert_func()
        self.db_int.conn.commit()

        result = self.db_inf.get_all_in_dict_without_id(test_table)
        self.assertEqual(expected_result, result)

    def _format_wrong_insert_test(self, insert_func, test_table, expected_rows):
        assertion_error = False  # If except is not activated then it should be false
        try:
            insert_func()
            self.db_int.conn.commit()
        except sqlite3.IntegrityError:
            assertion_error = True
            self.assertEqual(self.db_inf.count_rows(test_table), expected_rows)
        self.assertTrue(assertion_error, msg='No Integrity error')

    def test_a_InsertSong(self):
        def _insert():
            self.db_int.insert_song(data.track_single)

        self._format_correct_insert_test(_insert, 'song', data.song_table_single)

    def test_b_InsertTrack(self):
        def _insert():
            self.db_int.insert_track(1, data.track_single.spotify_id)

        self._format_correct_insert_test(_insert, 'track', data.track_table_single)

    def test_c_InsertTrackWithoutSong(self):
        def _insert():
            self.db_int.insert_track(2, data.track_multiple.spotify_id)

        self._format_wrong_insert_test(_insert, 'track', 1)

    def test_d_InsertArtist(self):
        def _insert():
            self.db_int.insert_artist(data.track_single.artist_tuple[0])

        self._format_correct_insert_test(_insert, 'artist', data.artist_table_single)

    def test_e_InsertSongArtist(self):
        def _insert():
            self.db_int.insert_song_artist(song_id=1, artist_id=1)

        self._format_correct_insert_test(_insert, 'song_artist', data.song_artist_table_single)

    def test_f_InsertSongArtistWithoutSong(self):
        def _insert():
            self.db_int.insert_song_artist(song_id=2, artist_id=1)

        self._format_wrong_insert_test(_insert, 'song_artist', 1)

    def test_g_InsertSongArtistWithoutArtist(self):
        def _insert():
            self.db_int.insert_song_artist(song_id=1, artist_id=2)

        self._format_wrong_insert_test(_insert, 'song_artist', 1)

    def test_h_InsertSongState(self):
        assert self.db_inf.get_all_in_dict('song')[0]['id'] == 1
        assert self.db_inf.get_all_in_dict('learning_state')[0]['id'] == 0

        def _insert():
            self.db_int.insert_song_state(song_id=1, learning_state_id=0, next_date=util.date_from_today(0))

        self._format_correct_insert_test(_insert, 'song_state', data.song_state_table)

    def test_i_InsertSongStateHistory(self):
        def _insert():
            pass

        self._format_correct_insert_test(_insert, 'song_state_history', data.song_state_hist_table)

    def test_j_InsertSongStateWithoutSong(self):
        def _insert():
            self.db_int.insert_song_state(song_id=2, learning_state_id=0, next_date='2022-01-01')

        self._format_wrong_insert_test(_insert, 'song_state', 1)

        db_inf2 = DatabaseInformation(self.db_conn.curs)
        self.assertEqual(db_inf2.count_rows('song_state_history'), 1)
        del db_inf2

    def test_k_InsertTag(self):
        def _insert():
            self.db_int.insert_tag(song_id=1, tag=data.tag_table[0]['tag'])

        self._format_correct_insert_test(_insert, 'tag', data.tag_table)

    def test_l_InsertTagWithoutSong(self):
        def _insert():
            self.db_int.insert_tag(song_id=2, tag='test')

        self._format_wrong_insert_test(_insert, 'tag', 1)

    def test_m_InsertSongPlaylist(self):
        input_and_result = {'song_id': 1, 'playlist_name': 'test'}

        def _insert():
            self.db_int.insert_song_playlist(**input_and_result)

        self._format_correct_insert_test(_insert, 'song_playlist', [input_and_result])


class TestDatabaseInsertTrack(unittest.TestCase):
    db_file = 'test_track.db'
    db_conn = DatabaseConnection(db_file)
    db_inf = DatabaseInformation(db_conn.curs)
    db_int = DatabaseInteraction(db_conn.curs, db_conn.conn)

    track = data.track_single
    song_table = data.song_table_single
    track_table = data.track_table_single
    artist_table = data.artist_table_single
    song_artist_table = data.song_artist_table_single
    song_state_table = data.song_state_table
    song_state_hist_table = data.song_state_hist_table
    tag_table = data.tag_table

    @classmethod
    def setUpClass(cls) -> None:
        cls.db_int.insert_single_track(cls.track, 0, 'test')
        cls.db_conn.conn.commit()

    @classmethod
    def tearDownClass(cls) -> None:
        """Delete database"""
        del cls.db_conn
        del cls.db_inf
        del cls.db_int
        os.remove(cls.db_file)

    def testSongTable(self):
        result = self.db_inf.get_all_in_dict_without_id('song')
        self.assertCountEqual(self.song_table, result)

    def testTrackTable(self):
        result = self.db_inf.get_all_in_dict_without_id('track')
        self.assertCountEqual(self.track_table, result)

    def testArtistTable(self):
        result = self.db_inf.get_all_in_dict_without_id('artist')
        self.assertCountEqual(self.artist_table, result)

    def testSongArtistTable(self):
        result = self.db_inf.get_all_in_dict_without_id('song_artist')
        self.assertCountEqual(self.song_artist_table, result)

    def testSongStateTable(self):
        result = self.db_inf.get_all_in_dict_without_id('song_state')
        self.assertCountEqual(self.song_state_table, result)

    def testSongStateHistoryTable(self):
        result = self.db_inf.get_all_in_dict_without_id('song_state_history')
        self.assertCountEqual(self.song_state_hist_table, result)

    def testTagTable(self):
        result = self.db_inf.get_all_in_dict_without_id('tag')
        self.assertCountEqual(self.tag_table, result)


class TestDatabaseInsertTrackMultipleArtists(TestDatabaseInsertTrack):
    db_file = 'test_track_multiple.db'
    db_conn = DatabaseConnection(db_file)
    db_inf = DatabaseInformation(db_conn.curs)
    db_int = DatabaseInteraction(db_conn.curs, db_conn.conn)

    track = data.track_multiple

    song_table = data.song_table_multiple
    track_table = data.track_table_multiple
    artist_table = data.artist_table_multiple
    song_artist_table = data.song_artist_table_multiple
    song_state_table = data.song_state_table
    song_state_hist_table = data.song_state_hist_table
    tag_table = data.tag_table


class TestDatabaseGetClass(unittest.TestCase):
    songset = SongSet({data.track_multiple, data.track_single})
    db_file = 'test_songset.db'
    db_conn = DatabaseConnection(db_file)
    db_inf = DatabaseInformation(db_conn.curs)
    db_int = DatabaseInteraction(db_conn.curs, db_conn.conn)

    @classmethod
    def setUpClass(cls) -> None:
        cls.db_int.insert_songset(cls.songset, 0, 'test')
        cls.db_int.insert_songs_in_playlist_db()
        cls.db_conn.conn.commit()
        cls.maxDiff = None

    @classmethod
    def tearDownClass(cls) -> None:
        """Delete database"""
        del cls.db_conn
        del cls.db_inf
        del cls.db_int
        os.remove(cls.db_file)

    def testGetSongSet(self):
        songset_result = self.db_inf.get_songset_all()
        self.assertEqual(self.songset, songset_result)

    def testLearningStates(self):
        for learning_state in learning_states:
            learning_state_via_db = self.db_inf.get_learning_state(learning_state.id)
            self.assertEqual(learning_state_via_db, learning_state)

    def testGetSongSetFromPlaylist(self):
        songset_result = self.db_inf.get_songset_from_playlist('first_check')
        self.assertEqual(self.songset, songset_result)

    def testGetPlaylists(self):
        playlists = self.db_inf.get_playlists()
        playlists_from_configs = [conf.playlist for conf in playlist_configs]
        self.assertListEqual(playlists, playlists_from_configs)

    def testGetPlaylistsConfigs(self):
        configs = self.db_inf.get_playlist_configs()
        configs_from_configs = [conf for conf in playlist_configs]
        for conf_conf in configs_from_configs:
            config_from_database = configs[conf_conf.playlist.name]
            self.assertEqual(config_from_database, conf_conf)

    def testGetPlaylistsConfigsFiltered(self):
        configs = self.db_inf.get_playlist_configs(only_filtered=True)
        configs_from_configs = [conf for conf in playlist_configs]
        for conf_conf in configs_from_configs:
            config_from_database = configs.get(conf_conf.playlist.name)
            if conf_conf.filters is None:
                self.assertIsNone(config_from_database)
            else:
                self.assertEqual(config_from_database, conf_conf)

    def testNumberTrackToAdd(self):
        configs = self.db_inf.get_playlist_configs(only_filtered=True)
        numbers_to_add_dict = self.db_inf.get_number_track_to_add_to_playlist(configs)
        for conf in configs.values():
            max_nr = conf.max_nr_of_tracks
            number_to_add = numbers_to_add_dict[conf.playlist.name]
            if conf.playlist.name == 'first_check':
                max_nr -= 2
            self.assertEqual(max_nr, number_to_add)

    def testTrackNumberInPlaylist(self):
        dict_number = self.db_inf.get_track_number_in_playlists()
        self.assertEqual(dict_number['first_check']['number'], 2)

    def getSongsToUpdateInserts(self):
        """More tests might be needed in the future"""
        add_dict = self.db_inf.get_songs_to_update_in_spotify('insert')
        self.assertEqual(add_dict[data.spotify_id_single], 'first_check')
        self.assertEqual(add_dict[data.spotify_id_multiple], 'first_check')


class TestUpdates(unittest.TestCase):
    songset = SongSet({data.track_multiple, data.track_single})
    songset_single = SongSet({data.track_single})
    songset_multiple = SongSet({data.track_multiple})
    songset_empty = SongSet({})
    db_file = 'test_update.db'
    db_conn = DatabaseConnection(db_file)
    db_inf = DatabaseInformation(db_conn.curs)
    db_int = DatabaseInteraction(db_conn.curs, db_conn.conn)
    sp_inf = SpotifyInformation(connect_spotify_from_config())

    table_column_dict = {'learning_information': ('next_date', 'learning_id', 'song_in_playlist'),
                         'song_playlist_information': ('playlist_name',),
                         'song_playlist_update_information': ('playlist_name', 'action')}

    @classmethod
    def setUpClass(cls) -> None:
        cls.db_int.insert_songset(cls.songset, 0, 'test')

    @classmethod
    def tearDownClass(cls) -> None:
        """Delete database"""
        del cls.db_conn
        del cls.db_inf
        del cls.db_int
        os.remove(cls.db_file)

    def testUpdatePlaylist(self):
        name = 'learn'
        spotify_id = 'fake_number'
        playlist = Playlist(name=name, spotify_id=spotify_id)
        self.db_int.update_playlist(playlist)
        playlists = self.db_inf.get_playlists()

        for playlist in playlists:
            if playlist.name == name:
                self.assertEqual(spotify_id, playlist.spotify_id)
            else:
                self.assertIsNone(playlist.spotify_id)

    def _test_update_format(self, table: str, expected_rows: int, columns: tuple = None, single_expect=(),
                            multiple_expect=None):
        if multiple_expect is None:
            multiple_expect = single_expect
        if columns is None:
            columns = self.table_column_dict[table]

        result_list = self.db_inf.get_all_in_dict(table)
        result_list = [result for result in result_list if result['song_id'] is not None]

        self.assertEqual(expected_rows, len(result_list), msg=f'Mistake for {table}')

        expect_dict = {data.title_single: single_expect, data.title_multiple: multiple_expect}

        for result_dict in result_list:
            expect = expect_dict[result_dict['title']]
            if len(expect) > 0:
                result = tuple(result_dict[column] for column in columns)
                self.assertEqual(expect, result, msg=f'Mistake for {table}')

    def _three_test_update_format(self, rows_learning=2, single_learning=(), multiple_learning=None,
                                  rows_song_playlist=0, single_song_playlist=(), multiple_song_playlist=None,
                                  rows_update=0, single_update=(), multiple_update=None):
        # Test song state (via learning_information)

        self._test_update_format('learning_information', expected_rows=rows_learning,
                                 single_expect=single_learning, multiple_expect=multiple_learning)

        # Test song playlist (via song_playlist_information)
        self._test_update_format('song_playlist_information', expected_rows=rows_song_playlist,
                                 single_expect=single_song_playlist, multiple_expect=multiple_song_playlist)

        # Test song playlist updates (via song_playlist_update_information)
        self._test_update_format('song_playlist_update_information', expected_rows=rows_update,
                                 single_expect=single_update, multiple_expect=multiple_update)

    def test_a_InsertSongsInPlaylist(self):
        self.db_int.insert_songs_in_playlist_db()
        self.db_conn.conn.commit()

        single_learning = (util.date_from_today(0), 0, 1)
        single_song_playlist = ('first_check',)
        self._three_test_update_format(single_learning=single_learning,
                                       rows_song_playlist=2, single_song_playlist=single_song_playlist,
                                       rows_update=2)

        self.db_int.delete_from_song_playlist_update(self.songset)
        self.db_conn.conn.commit()

        self._three_test_update_format(single_learning=single_learning,
                                       rows_song_playlist=2, single_song_playlist=single_song_playlist,
                                       rows_update=0)

    def test_b_Unknown(self):
        self.db_int.update_unknown_songset(self.songset)
        self.db_conn.conn.commit()

        single_learning = (util.date_from_today(0), 2, 0)
        single_update = ('first_check', 'delete')
        self._three_test_update_format(single_learning=single_learning,
                                       rows_song_playlist=0,
                                       rows_update=2, single_update=single_update)

        self.db_int.delete_from_song_playlist_update(self.songset)
        self.db_int.insert_songs_in_playlist_db()

        single_learning = (util.date_from_today(0), 2, 1)
        single_update = ('first_learn', 'insert')
        single_song_playlist = ('first_learn',)
        self._three_test_update_format(single_learning=single_learning,
                                       rows_song_playlist=2, single_song_playlist=single_song_playlist,
                                       rows_update=2, single_update=single_update)

        self.db_int.delete_from_song_playlist_update(self.songset)
        self.db_conn.conn.commit()

    def test_c_Unknown(self):
        self.db_int.update_unknown_songset(self.songset)
        self.db_conn.conn.commit()

        single_learning = (util.date_from_today(0), 2, 1)
        single_song_playlist = ('first_learn',)
        self._three_test_update_format(single_learning=single_learning,
                                       rows_song_playlist=2, single_song_playlist=single_song_playlist,
                                       rows_update=0)

        self.db_int.delete_from_song_playlist_update(self.songset)
        self.db_int.insert_songs_in_playlist_db()

        self._three_test_update_format(single_learning=single_learning,
                                       rows_song_playlist=2, single_song_playlist=single_song_playlist,
                                       rows_update=0)

        self.db_int.delete_from_song_playlist_update(self.songset)
        self.db_conn.conn.commit()

    def test_d_Known(self):
        self.db_int.update_known_songset(self.songset)
        self.db_conn.conn.commit()

        single_learning = (util.date_from_today(1), 3, 0)
        single_update = ('first_learn', 'delete')

        self._three_test_update_format(single_learning=single_learning,
                                       rows_song_playlist=0,
                                       rows_update=2, single_update=single_update)

        self.db_int.delete_from_song_playlist_update(self.songset)
        self.db_int.insert_songs_in_playlist_db()

        self._three_test_update_format(single_learning=single_learning,
                                       rows_song_playlist=0,
                                       rows_update=0)

        self.db_int.change_next_date_to_today(self.songset)
        self.db_int.insert_songs_in_playlist_db()
        self.db_conn.conn.commit()

        single_learning = (util.date_from_today(0), 3, 1)
        single_song_playlist = ('test',)
        single_update = ('test', 'insert')
        self._three_test_update_format(single_learning=single_learning,
                                       rows_song_playlist=2, single_song_playlist=single_song_playlist,
                                       rows_update=2, single_update=single_update)

        self.db_int.delete_from_song_playlist_update(self.songset)
        self.db_conn.conn.commit()

    def test_e_Unknown_single(self):
        self.db_int.update_unknown_songset(self.songset_single)
        self.db_conn.conn.commit()

        single_learning = (util.date_from_today(0), 2, 0)
        multiple_learning = (util.date_from_today(0), 3, 1)
        multiple_song_playlist = ('test',)
        single_update = ('test', 'delete')
        self._three_test_update_format(single_learning=single_learning, multiple_learning=multiple_learning,
                                       rows_song_playlist=1, multiple_song_playlist=multiple_song_playlist,
                                       rows_update=1, single_update=single_update)

        self.db_int.delete_from_song_playlist_update(self.songset)
        self.db_int.insert_songs_in_playlist_db()

        single_learning = (util.date_from_today(0), 2, 1)
        multiple_learning = (util.date_from_today(0), 3, 1)
        single_song_playlist = ('first_learn',)
        multiple_song_playlist = ('test',)
        single_update = ('first_learn', 'insert')
        self._three_test_update_format(single_learning=single_learning, multiple_learning=multiple_learning,
                                       rows_song_playlist=2, single_song_playlist=single_song_playlist,
                                       multiple_song_playlist=multiple_song_playlist,
                                       rows_update=1, single_update=single_update)

        self.db_int.delete_from_song_playlist_update(self.songset)
        self.db_conn.conn.commit()

    def test_f_known_multiple(self):
        self.db_int.update_known_songset(self.songset_multiple)
        self.db_conn.conn.commit()

        single_learning = (util.date_from_today(0), 2, 1)
        multiple_learning = (util.date_from_today(1), 1, 0)
        single_song_playlist = ('first_learn',)
        multiple_update = ('test', 'delete')
        self._three_test_update_format(single_learning=single_learning, multiple_learning=multiple_learning,
                                       rows_song_playlist=1, single_song_playlist=single_song_playlist,
                                       rows_update=1, multiple_update=multiple_update)

        self.db_int.delete_from_song_playlist_update(self.songset)
        self.db_int.insert_songs_in_playlist_db()

        self._three_test_update_format(single_learning=single_learning, multiple_learning=multiple_learning,
                                       rows_song_playlist=1, single_song_playlist=single_song_playlist,
                                       rows_update=0)

        self.db_int.change_next_date_to_today(self.songset_multiple)
        self.db_int.insert_songs_in_playlist_db()
        self.db_conn.conn.commit()

        multiple_learning = (util.date_from_today(0), 1, 1)
        single_song_playlist = ('first_learn',)
        multiple_song_playlist = ('check',)
        multiple_update = ('check', 'insert')
        self._three_test_update_format(single_learning=single_learning, multiple_learning=multiple_learning,
                                       rows_song_playlist=2, single_song_playlist=single_song_playlist,
                                       multiple_song_playlist=multiple_song_playlist,
                                       rows_update=1, multiple_update=multiple_update)

        self.db_int.delete_from_song_playlist_update(self.songset)
        self.db_conn.conn.commit()

    def test_g_known_empty(self):
        self.db_int.update_known_songset(self.songset_empty)
        self.db_conn.conn.commit()

    def test_h_unknown_empty(self):
        self.db_int.update_known_songset(self.songset_empty)
        self.db_conn.conn.commit()

    def test_i_repeat(self):
        self.db_int.update_repeat_songset(self.songset)
        self.db_conn.conn.commit()

        single_learning = (util.date_from_today(0), 2, 0)
        multiple_learning = (util.date_from_today(1), 1, 0)
        single_update = ('first_learn', 'delete')
        multiple_update = ('check', 'delete')
        self._three_test_update_format(single_learning=single_learning, multiple_learning=multiple_learning,
                                       rows_song_playlist=0,
                                       rows_update=2, single_update=single_update, multiple_update=multiple_update)

        self.db_int.insert_songs_in_playlist_db()
        self.db_conn.conn.commit()

    def test_j_get_update_set_for_spotify(self):
        playlist_fl = Playlist('first_learn')
        playlist_check = Playlist('check')
        dict_expect = {'delete': {playlist_fl: self.songset_single, playlist_check: self.songset_multiple},
                       'insert': {playlist_fl: self.songset_single}}
        dict_actual = self.db_inf.get_songset_to_update_in_spotify()

        self.assertDictEqual(dict_expect, dict_actual)

    def test_z_Remove(self):
        self.db_int.remove_songset(self.songset)
        self.db_conn.conn.commit()

        result = self.db_inf.get_all_in_dict('track')
        for track_row in result:
            self.assertEqual(track_row['active'], 0)

    def test_second_insert_song(self):
        pass

# class TestSelect(unittest.TestCase):
#     db_conn = None
#     db_file = 'test.db'
#     songset = SongSet({data.track_multiple, data.track_single})
#     songset_single = SongSet({data.track_single})
#     songset_multiple = SongSet({data.track_multiple})
