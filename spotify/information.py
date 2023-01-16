from spotify.connection import connect_spotify_from_config
from data_classes import *
from util import first_timestamp_higher_bool


class Iterator:
    def __init__(self, connection, *args, **kwargs):
        self._sp_conn = connection
        self._iterator = self._get_iterator(*args, **kwargs)
        self._item_class = self._get_item_class()

    def _get_iterator(self, *args, **kwargs):
        raise NotImplementedError

    def _get_item_class(self):
        raise NotImplementedError

    def _transform_items_to_class(self):
        raise NotImplementedError

    def get_results(self):
        return self._transform_items_to_class()

    def __getitem__(self, key):
        return self._iterator[key]

    def __next__(self):
        self._iterator = self._sp_conn.next(self._iterator)


##############################################################
class PlaylistIterator(Iterator):
    def _get_iterator(self):
        return self._sp_conn.current_user_playlists()

    def _get_item_class(self):
        return Playlist.from_spotify_playlist_dict

    def _transform_items_to_class(self):
        return [self._item_class(item_dict) for item_dict in self['items']]


##############################################################
class TrackIterator(Iterator):
    def _transform_items_to_class(self) -> SongSet:
        return SongSet({self._item_class(item_dict) for item_dict in self['items']})

    def _get_iterator(self, *args, **kwargs):
        raise NotImplementedError

    def _get_item_class(self):
        raise NotImplementedError


##############################################################
class SearchTrackIterator(TrackIterator):
    def _get_iterator(self, query, limit):
        return self._sp_conn.search(query, limit)['tracks']

    def _get_item_class(self):
        return Track.from_spotify_track_dict

    def __next__(self):
        self._iterator = self._sp_conn.next(self._iterator)['tracks']


##############################################################
class PlayedTrackIterator(TrackIterator):
    def _get_iterator(self):
        return self._sp_conn.current_user_recently_played()

    def _get_item_class(self):
        return Track.from_spotify_played_track_dict

    # Not possible in spotify API to get further than first dict
    __next__ = None


##############################################################
class PlaylistTrackIterator(TrackIterator):
    def _get_iterator(self, playlist: Playlist):
        assert playlist.spotify_id is not None, f'{playlist}'
        return self._sp_conn.playlist_items(playlist.spotify_id)

    def _get_item_class(self):
        return Track.from_spotify_playlist_track_dict


##############################################################
class SpotifyInformation:
    def __init__(self, spotify_connection):
        self.conn = spotify_connection

    def get_relevant_playlists(self) -> list[Playlist]:
        """Returns all personal playlists in Spotify."""
        playlist_iterator = PlaylistIterator(self.conn)
        playlist_list = playlist_iterator.get_results()

        while playlist_iterator['next']:
            next(playlist_iterator)
            playlist_list.extend(playlist_iterator.get_results())
        return playlist_list

    def get_playlist_from_playlist(self, playlist, playlist_list: list[Playlist] = None) -> Playlist:
        """Can be used to add spotify_id, if that is unknown."""
        if playlist_list is None:
            playlist_list = self.get_relevant_playlists()
        playlist_name_list = [playlist_inst for playlist_inst in playlist_list if playlist.name == playlist_inst.name]
        if len(playlist_name_list) == 0:
            return playlist
        assert len(playlist_name_list) == 1, f'There are multiple playlists with the same name: {playlist_name_list}'
        return playlist_name_list[0]

    def get_playlist_from_spotify_id(self, spotify_id: str) -> Playlist:
        spotify_playlist_dict = self.conn.playlist(spotify_id)
        playlist = Playlist.from_spotify_playlist_dict(spotify_playlist_dict)
        return playlist

    def get_track_from_spotify_id(self, spotify_id) -> Track:
        spotify_track_dict = self.conn.track(spotify_id)
        return Track.from_spotify_track_dict(spotify_track_dict)

    def get_songset_from_search_query(self, query, limit=10) -> SongSet:
        max_iteration_step = min(limit, 50)  # 50 is maximum given from Spotify

        search_iterator = SearchTrackIterator(self.conn, query=query, limit=max_iteration_step)
        songset = search_iterator.get_results()
        while search_iterator['next'] and limit > max_iteration_step:
            max_iteration_step = min(limit, 50)
            limit -= max_iteration_step
            next(search_iterator)
            songset.extend(search_iterator.get_results()[0:max_iteration_step])
        return songset

    def get_last_played_tracks(self) -> SongSet:
        played_iterator = PlayedTrackIterator(self.conn)
        played_songset = played_iterator.get_results()
        return played_songset

    def get_last_played_tracks_since(self, timestamp) -> SongSet:
        songset_last_played = self.get_last_played_tracks()
        track_list = {track for track in songset_last_played if first_timestamp_higher_bool(track.played_at, timestamp)}
        return SongSet(track_list)

    def get_songset_from_playlist(self, playlist: Playlist) -> SongSet:
        result_iterator = PlaylistTrackIterator(self.conn, playlist)
        songset = result_iterator.get_results()

        while result_iterator['next']:
            next(result_iterator)
            songset.extend(result_iterator.get_results())
        return songset

