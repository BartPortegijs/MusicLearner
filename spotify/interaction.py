from spotify.information import SpotifyInformation
from data_classes import *
import util


class PlaylistInteraction:
    def __init__(self, spotify_connection, playlist):
        self._conn = spotify_connection
        self.playlist = self.update_playlist_id(playlist)
        self._spotify_id = self.playlist.spotify_id

    def update_playlist_id(self, playlist: Playlist) -> Playlist:
        if playlist.spotify_id is None:
            return SpotifyInformation(self._conn).get_playlist_from_playlist(playlist)
        return playlist

    def delete_playlist(self):
        self._conn.current_user_unfollow_playlist(playlist_id=self._spotify_id)

    def add_songset(self, songset: SongSet):
        track_id_list = songset.get_track_ids()
        for track_ids_chunk in util.split_into_chunks(track_id_list, 100):
            self._conn.playlist_add_items(self._spotify_id, track_ids_chunk)

    def remove_songset(self, songset: SongSet):
        track_id_list = songset.get_track_ids()
        for track_ids_chunk in util.split_into_chunks(list_to_split=track_id_list, chunk_size=100):
            self._conn.playlist_remove_all_occurrences_of_items(self._spotify_id, track_ids_chunk)

    def clear_playlist(self):
        songlist = SpotifyInformation(self._conn).get_songset_from_playlist(self.playlist)
        self.remove_songset(songlist)

    @classmethod
    def create_playlist(cls, spotify_connection, playlist):
        user_id = spotify_connection.me()['id']
        spotify_connection.user_playlist_create(user=user_id, name=playlist.name, public='False')
        return cls(spotify_connection, playlist)
