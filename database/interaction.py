from dataclasses import asdict
import logging

from data_classes import *
from database.information import DatabaseInformation
from util import date_from_today


##############################################################
class DatabaseInteraction:
    def __init__(self, cursor, conn):
        self.cursor = cursor
        self.conn = conn
        self.db_inf = DatabaseInformation(cursor)

    def commit(self):
        self.conn.commit()

    def _insert_structure(self, select_query, insert_query, data_dict):
        """Standard format for inserting data. The select query checks if the row that needs inserting already exists.
        If so, it returns that id, and the insert query is not executed. If the row doesn't exist, it executes
        the insert query. The data dict has values that need to be inserted in the queries."""
        if select_query is None:
            result = None
        else:
            result = self.db_inf.query_to_list_dict(select_query, data_dict)
        if result:
            result_id = result[0]['id']
        else:
            self.cursor.execute(insert_query, data_dict)
            result_id = self.cursor.lastrowid
        return result_id
    
    def insert_learning_state(self, learning_state):
        data_dict = asdict(learning_state)
        select_query = "SELECT id FROM learning_state WHERE id = :id LIMIT 1"
        insert_query = """INSERT INTO learning_state(id, phase, activity, next_id_positive, next_id_negative, days_before_active) 
                            VALUES(:id, :phase, :activity, :next_id_positive, :next_id_negative, :days_before_active);"""
        return self._insert_structure(select_query, insert_query, data_dict)

    def insert_playlist(self, playlist):
        """Add test still"""
        data_dict = asdict(playlist)
        select_query = "SELECT id FROM playlist WHERE name = :name LIMIT 1"
        insert_query = """INSERT INTO playlist(name, spotify_id) VALUES(:name, :spotify_id);"""
        return self._insert_structure(select_query, insert_query, data_dict)
    
    def insert_playlist_rule(self, playlist_id, config_rule):
        """Add test still"""
        data_dict = asdict(config_rule) | {'playlist_id': playlist_id}
        select_query = None
        if config_rule.config_type != 'filter':
            select_query = """SELECT id FROM playlist_config WHERE playlist_id = :playlist_id AND 
                            config_type = :config_type"""
        insert_query = """INSERT INTO playlist_config(playlist_id, config_type, variable, sign, value) 
                            VALUES(:playlist_id, :config_type, :variable, :sign, :value);"""
        return self._insert_structure(select_query, insert_query, data_dict)

    def insert_song(self, track):
        data_dict = asdict(track)
        select_query = "SELECT id FROM song WHERE lower(title) = lower(:title) AND lower(artists) = lower(:artist) " \
                       "LIMIT 1"
        insert_query = "INSERT INTO song(title, artists) VALUES(:title, :artist)"
        return self._insert_structure(select_query, insert_query, data_dict)

    def insert_track(self, song_id, spotify_track_id):
        data_dict = locals()
        select_query = "SELECT id FROM track WHERE spotify_track_id = :spotify_track_id LIMIT 1"
        insert_query = """INSERT INTO track(song_id, spotify_track_id, active) 
                           VALUES(:song_id, :spotify_track_id, 1)"""
        return self._insert_structure(select_query, insert_query, data_dict)

    def insert_artist(self, artist):
        data_dict = asdict(artist)
        select_query = "SELECT id FROM artist WHERE spotify_artist_id = :spotify_id LIMIT 1"
        insert_query = "INSERT INTO artist(name, spotify_artist_id) VALUES(:name, :spotify_id)"
        return self._insert_structure(select_query, insert_query, data_dict)

    def insert_song_artist(self, song_id, artist_id):
        data_dict = locals()
        select_query = "SELECT id FROM song_artist WHERE song_id = :song_id AND artist_id = :artist_id LIMIT 1"
        insert_query = "INSERT INTO song_artist(song_id, artist_id) VALUES(:song_id, :artist_id)"
        return self._insert_structure(select_query, insert_query, data_dict)
    
    def insert_song_state(self, song_id, learning_state_id, next_date):
        data_dict = locals()
        select_query = "SELECT id FROM song_state WHERE song_id = :song_id LIMIT 1"
        insert_query = "INSERT INTO song_state(song_id, learning_state_id, song_in_playlist, next_date) " \
                       "VALUES(:song_id, :learning_state_id, 0, :next_date)"
        return self._insert_structure(select_query, insert_query, data_dict)

    def insert_tag(self, song_id, tag):
        data_dict = locals()
        select_query = "SELECT id FROM tag WHERE song_id = :song_id AND tag = :tag LIMIT 1"
        insert_query = "INSERT INTO tag(song_id, tag) VALUES(:song_id, :tag)"
        return self._insert_structure(select_query, insert_query, data_dict)

    def insert_song_playlist(self, song_id, playlist_name):
        data_dict = locals()
        select_query = "SELECT id FROM song_playlist " \
                       "WHERE song_id = :song_id AND playlist_name = :playlist_name LIMIT 1"
        insert_query = "INSERT INTO song_playlist(song_id, playlist_name) VALUES(:song_id, :playlist_name)"
        return self._insert_structure(select_query, insert_query, data_dict)
    
    ##############################################################
    def insert_songset(self, songset: SongSet, next_state: int, tag=None):
        for track in songset:
            self.insert_single_track(track, next_state, tag, next_date=None)
    
    def insert_single_track(self, track, state_id, tag, next_date):
        song_id = self.insert_song(track)
        if tag is not None:
            self.insert_tag(song_id, tag)

        if state_id == -1:
            return

        self.insert_track(song_id, track.spotify_id)

        for artist in track.artist_tuple:
            artist_id = self.insert_artist(artist)
            self.insert_song_artist(song_id, artist_id)

        current_state = self.db_inf.get_learning_state(state_id)
        if next_date is None:
            next_date = date_from_today(days=current_state.days_before_active)

        self.insert_song_state(song_id, state_id, next_date)
        if tag is not None:
            self.insert_tag(song_id, tag)
    
    def insert_playlist_config(self, playlist_config: PlaylistConfig):
        assert type(playlist_config) == PlaylistConfig
        playlist_id = self.insert_playlist(playlist_config.playlist)
        if playlist_config.rules is not None:
            [self.insert_playlist_rule(playlist_id, config_rule) for config_rule in playlist_config.rules]
    
    def update_playlist(self, playlist: Playlist):
        update_query = f"""
        UPDATE playlist
        SET spotify_id = '{playlist.spotify_id}'
        WHERE name = '{playlist.name}'"""
        self.cursor.execute(update_query)
    
    ##############################################################
    def insert_songs_in_playlist_db(self, update_configs: list[PlaylistConfig, ...]):
        playlist_config_dict = {playlist_conf.playlist.name: playlist_conf for playlist_conf in update_configs}
        numbers_to_add_dict = self.db_inf.get_number_track_to_add_to_playlist(playlist_config_dict)

        for config in playlist_config_dict.values():
            limit = numbers_to_add_dict[config.playlist.name]
            if limit is None or limit > 0:
                query, insert_dict = config.create_filter_select_query(limit)
                result = self.db_inf.query_to_list_dict(query, insert_dict)

                query = "UPDATE song_state SET song_in_playlist = 1 WHERE song_id= :song_id"

                for row in result:
                    self.insert_song_playlist(**row)
                    self.cursor.execute(query, row)
                    logging.info(f'Insert {row}')

    def remove_songset(self, songset):
        update_script = "DELETE FROM track WHERE spotify_track_id = ?"
        remove_script = "DELETE FROM song_playlist WHERE song_id = ?"
        state_update_script = "UPDATE song_state SET song_in_playlist = 0 WHERE song_id = ?"

        song_ids = self.db_inf.get_song_ids_from_songset(songset)

        for track in songset:
            spotify_id = track.spotify_id
            self.cursor.execute(update_script, (spotify_id,))

        self.cursor.executemany(remove_script, song_ids)
        self.cursor.executemany(state_update_script, song_ids)

    def update_repeat_songset(self, songset):
        song_ids = self.db_inf.get_song_ids_from_songset(songset)

        remove_script = "DELETE FROM song_playlist WHERE song_id = ?"
        state_update_script = f"""
                                UPDATE song_state
                                SET song_in_playlist = 0,
                                    next_date = DATE('now', 'localtime', (MIN(7, days_before_active)  || ' day'))
                                FROM learning_information
                                WHERE song_state.song_id = ?
                                    AND song_state.song_id = learning_information.song_id """

        self.cursor.executemany(remove_script, song_ids)
        self.cursor.executemany(state_update_script, song_ids)

    def update_known_songset(self, songset):
        self.update_songset(songset, update_type='positive')

    def update_unknown_songset(self, songset):
        self.update_songset(songset, update_type='negative')
    
    def update_songset(self, songset, update_type):
        assert update_type in ('positive', 'negative')
        song_ids = self.db_inf.get_song_ids_from_songset(songset)
        select_query = f"""SELECT song_id FROM learning_information 
                            WHERE song_id = ? AND next_id_{update_type} IS NOT NULL"""
        song_ids_updatable = []
        for song_id in song_ids:
            result = self.db_inf.query_to_list_dict(select_query, song_id)
            if len(result) > 0:
                song_ids_updatable.append((result[0]['song_id'],))

        remove_script = f"""DELETE FROM song_playlist WHERE song_id = ?"""
        state_update_script = f"""
                        UPDATE song_state
                        SET learning_state_id = learning_information.next_id_{update_type},
                            song_in_playlist = 0,
                            next_date = DATE('now', 'localtime', (days_before_active_{update_type}  || ' day'))
                        FROM learning_information
                        WHERE song_state.song_id = ?
                            AND song_state.song_id = learning_information.song_id """

        self.cursor.executemany(remove_script, song_ids_updatable)
        self.cursor.executemany(state_update_script, song_ids_updatable)
    
    ##############################################################
    # def delete_from_song_playlist(self, songset):
    #     song_ids = self.db_inf.get_song_ids_from_songset(songset)
    #     remove_script = "DELETE FROM song_playlist WHERE song_id = ?"
    #     self.cursor.executemany(remove_script, song_ids)

    def delete_from_song_playlist_update(self, songset, action=None):
        song_ids = self.db_inf.get_song_ids_from_songset(songset)
        remove_script = "DELETE FROM song_playlist_update WHERE song_id = ?"
        if action is not None:
            remove_script += f" AND action = '{action}'"
        self.cursor.executemany(remove_script, song_ids)

    def change_next_date_to_today(self, songset):
        """This function exists for testing purposes."""
        song_ids = self.db_inf.get_song_ids_from_songset(songset)
        update_script = """UPDATE song_state SET next_date = DATE('now') WHERE song_id= ?"""
        self.cursor.executemany(update_script, song_ids)
