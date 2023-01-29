from data_classes import *
import logging


class DatabaseInformation:
    def __init__(self, cursor):
        self.cursor = cursor

    def query_to_list_dict(self, select_query, filter_dict: Union[list, dict] = None):
        if filter_dict is None:
            data = self.cursor.execute(select_query)
        else:
            data = self.cursor.execute(select_query, filter_dict)
        rows = self.cursor.fetchall()
        columns = [column[0] for column in data.description]
        return self._result_to_dict(columns, rows)

    def _result_to_dict(self, column_list, rows):
        """Creates a list of dictionaries. All dictionaries have a column, value structure."""
        return [self._row_tuple_to_dict(column_list, row) for row in rows]

    @staticmethod
    def _row_tuple_to_dict(column_list, row):
        return {col: value for col, value in zip(column_list, row)}

    def _query_to_list_dict_with_lookup(self, key, select_query, filter_dict={}):
        dict_rows = self.query_to_list_dict(select_query, filter_dict)
        return {dict_row[key]: dict_row for dict_row in dict_rows}

    def get_column_values(self, select_query, column, filter_dict={}):
        """From a list with dictionaries with only one column, select all the values."""
        result = self.query_to_list_dict(select_query, filter_dict)
        return {table_tuple[column] for table_tuple in result}

    def get_names(self, types):
        assert types in ('table', 'view')
        select_query = f"SELECT name FROM sqlite_master WHERE type='{types}';"
        return self.get_column_values(select_query, 'name')

    def count_rows(self, table):
        select_query = f"SELECT COUNT(*) AS count FROM {table};"
        return list(self.get_column_values(select_query, 'count'))[0]

    def get_all_in_dict(self, table):
        select_query = f"SELECT * FROM {table};"
        return self.query_to_list_dict(select_query)

    def get_all_in_dict_without_id(self, table):
        dict_result = self.get_all_in_dict(table)
        result = []
        for dict_row in dict_result:
            result.append({k: v for k, v in dict_row.items() if k != 'id'})
        return result

    ##############################################################
    def get_learning_state(self, learning_state_id):
        data_dict = locals()
        select_query = "SELECT * FROM learning_state WHERE id = :learning_state_id"
        learning_state_table_dict = self.query_to_list_dict(select_query, data_dict)
        current_state = LearningState(**learning_state_table_dict[0])
        return current_state

    def get_songset_all(self):
        select_query = """SELECT * FROM track_information"""
        track_table_dict = self.query_to_list_dict(select_query)
        return self._get_songset(track_table_dict)

    def get_songset_from_song_ids(self, song_ids: list):
        select_query = f"""SELECT * FROM track_information WHERE song_id in ({','.join(['?'] * len(song_ids))})"""
        track_table_dict = self.query_to_list_dict(select_query, song_ids)
        return self._get_songset(track_table_dict)

    def get_songset_from_playlist(self, playlist_name):
        data_dict = locals()
        select_query = """
            SELECT ti.*
            FROM song_playlist_information pi
            INNER JOIN track_information ti
                ON pi.song_id = ti.song_id
            WHERE pi.playlist_name=:playlist_name"""
        track_table_dict = self.query_to_list_dict(select_query, data_dict)
        return self._get_songset(track_table_dict)

    def _get_songset(self, track_information_table_dict):
        songset = SongSet(set(self.get_track_from_row(row) for row in track_information_table_dict))
        return songset

    artist_tuple = tuple[Artist, ...]

    def get_track_from_row(self, row):
        id_song = row['song_id']
        artist = self.get_artists_from_song_id(id_song)
        return Track(artist=row['artists'], title=row['title'], artist_tuple=artist,
                     spotify_id=row['spotify_track_id'], song_id=id_song)

    def get_artists_from_song_id(self, song_id) -> artist_tuple:
        select_query = """SELECT
                            *,
                            name,
                            spotify_artist_id
                        FROM song_artist
                        LEFT JOIN artist
                            ON song_artist.artist_id = artist.id
                        WHERE song_id= ?"""
        result = self.query_to_list_dict(select_query, (song_id,))
        return tuple(Artist(row['name'], row['spotify_artist_id']) for row in result)

    def get_playlists(self):
        playlist_dict = self.get_all_in_dict('playlist')
        return [Playlist(playlist['name'], playlist['spotify_id']) for playlist in playlist_dict]

    def get_playlist_configs(self, only_filtered=False) -> dict:
        playlists = self.get_playlists()
        config_rows = self.get_all_in_dict('playlist_config_information')

        # Split the config table into different groups per playlist
        playlist_dict = {playlist.name: [] for playlist in playlists}
        for row in config_rows:
            playlist_dict[row['playlist_name']].append(row)

        playlist_confs = [self.get_single_playlist_config(playlist_conf_rows) for playlist_conf_rows in
                          playlist_dict.values()]
        if only_filtered:
            return {playlist_conf.playlist.name: playlist_conf
                    for playlist_conf in playlist_confs if playlist_conf.filters is not None}
        return {playlist_conf.playlist.name: playlist_conf for playlist_conf in playlist_confs}

    @staticmethod
    def get_single_playlist_config(playlist_rows: list[dict]):
        playlist = Playlist(spotify_id=playlist_rows[0]['spotify_id'], name=playlist_rows[0]['playlist_name'])

        config_rules = []
        for row in playlist_rows:
            config_rules.append(ConfigRule(config_type=row['config_type'], variable=row['variable'], sign=row['sign'],
                                           value=row['value']))
        return PlaylistConfig(playlist=playlist, rules=config_rules)

    def get_number_track_to_add_to_playlist(self, playlist_configs):
        configs_names = [config_name for config_name in playlist_configs.keys()]
        number_dict = {k: v for k, v in self.get_track_number_in_playlists().items() if k in configs_names}

        logging.info(f'Current numbers in playlists {number_dict}')
        numbers_to_add_dict = {}
        for playlist_config in playlist_configs.values():
            name = playlist_config.playlist.name
            songs_in_playlist = number_dict[name]['number']
            max_number = playlist_config.max_nr_of_tracks
            if max_number:
                numbers_to_add_dict[name] = max_number - songs_in_playlist
            else:
                numbers_to_add_dict[name] = None
        logging.info(f'Numbers to add in playlists {numbers_to_add_dict}')
        return numbers_to_add_dict

    def get_track_number_in_playlists(self):
        query = "SELECT COUNT(song_id) AS number, playlist_name FROM song_playlist_information GROUP BY playlist_name"
        return self._query_to_list_dict_with_lookup(select_query=query, key='playlist_name')

    def get_songs_to_update_in_spotify(self):
        """Returns dictionary for all ids to add to which playlist."""
        rows = self.get_all_in_dict('song_playlist_update_information')
        return {action: {row['spotify_track_id']: row['name'] for row in rows if row['action'] == action}
                for action in ('delete', 'insert')}

    def get_songset_to_update_in_spotify(self):
        """Returns dictionary for all playlist and what songset to add."""
        rows = self.get_all_in_dict('song_playlist_update_information')
        action_dict = {'delete': dict(), 'insert': dict()}

        for row in rows:
            action = row['action']
            playlist = Playlist(row['playlist_name'], row['spotify_playlist_id'])
            song = self.get_songset_from_song_ids([row['song_id']])
            if action_dict[action].get(playlist) is None:
                action_dict[action][playlist] = SongSet(set())
            action_dict[action][playlist].extend(song)
        return action_dict

    def get_song_ids_from_songset(self, songset: SongSet):
        song_ids = []

        query = """SELECT 
                        song.id AS song_id
                    FROM song
                    INNER JOIN track 
                    ON song.id = track.song_id
                    WHERE track.spotify_track_id = :spotify_id
                    AND track.active=1"""
        for track in songset:
            filter_dict = {'spotify_id': track.spotify_id}
            result_temp = self.query_to_list_dict(query, filter_dict)
            try:
                song_ids.append((result_temp[0]['song_id'],))
            except IndexError:
                raise Exception(f'Track {track} does not exist in database. {result_temp}')
        return song_ids
