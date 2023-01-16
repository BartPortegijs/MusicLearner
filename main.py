import util
from database.connection import DatabaseConnection
from database.information import DatabaseInformation
from database.interaction import DatabaseInteraction
from spotify.connection import connect_spotify_from_config
from spotify.interaction import PlaylistInteraction
from spotify.information import SpotifyInformation


def main():
    with DatabaseConnection('music_learner.db') as (curs, conn):
        db_inf = DatabaseInformation(curs)
        db_int = DatabaseInteraction(curs, conn)
        spotify_connection = connect_spotify_from_config()
        sp_inf = SpotifyInformation(spotify_connection)

        connection_classes = {'spotify_connection': spotify_connection, 'sp_inf': sp_inf,
                              'db_inf': db_inf, 'db_int': db_int}

        create_playlists_from_database(**connection_classes)
        remove_configs, repeat_configs, insert_configs, update_configs = split_playlist_types(**connection_classes)

        insert_new_songs_to_db(insert_configs, **connection_classes)
        remove_songs_from_db(remove_configs, **connection_classes)
        repeat_songs_from_db(repeat_configs, **connection_classes)
        update_songs_in_db(update_configs, **connection_classes)
        db_int.insert_songs_in_playlist_db()

        update_tracks_in_spotify(**connection_classes)
        conn.commit()


def create_playlists_from_database(spotify_connection, db_inf, db_int, sp_inf, **kwargs):
    """Create the playlists in Spotify as defined in the database."""
    spotify_playlists = sp_inf.get_relevant_playlists()
    for playlist in db_inf.get_playlists():

        # Checks if database has spotify_id, and otherwise add spotify_id for existing spotify playlists
        if playlist.spotify_id is None:
            playlist = sp_inf.get_playlist_from_playlist(playlist, playlist_list=spotify_playlists)
            db_int.update_playlist(playlist)

        # If after previous check, there is still no spotify_id, we should create playlist in spotify.
        if playlist.spotify_id is None:
            sp_int = PlaylistInteraction(spotify_connection, playlist)
            playlist_spotify = sp_int.create_playlist(spotify_connection, playlist)
            db_int.update_playlist(playlist_spotify.playlist)


def split_playlist_types(db_inf, **kwargs):
    remove_configs, repeat_configs, insert_configs, update_configs = [], [], [], []
    for config in db_inf.get_playlist_configs().values():
        if config.remove:
            remove_configs.append(config)
        elif config.repeat:
            repeat_configs.append(config)
        elif type(config.introduction_state) == int:
            insert_configs.append(config)
        else:
            update_configs.append(config)
    return remove_configs, repeat_configs, insert_configs, update_configs


def _structure_song_action(config, sp_inf: SpotifyInformation):
    songset = sp_inf.get_songset_from_playlist(config.playlist)
    pl_int = PlaylistInteraction(sp_inf.conn, config.playlist)
    pl_int.clear_playlist()
    return songset


def insert_new_songs_to_db(insert_configs: list, sp_inf: SpotifyInformation, db_int: DatabaseInteraction, **kwargs):
    for config in insert_configs:
        songset_insert = _structure_song_action(config, sp_inf)
        db_int.insert_songset(songset_insert, next_state=config.introduction_state, tag=config.introduction_tag)


def remove_songs_from_db(remove_configs: list, sp_inf: SpotifyInformation, db_int: DatabaseInteraction, **kwargs):
    for config in remove_configs:
        songset_remove = _structure_song_action(config, sp_inf)
        db_int.remove_songset(songset_remove)


def repeat_songs_from_db(repeat_configs: list, sp_inf: SpotifyInformation, db_int: DatabaseInteraction, **kwargs):
    for config in repeat_configs:
        songset_repeat = _structure_song_action(config, sp_inf)
        db_int.update_repeat_songset(songset_repeat)


def update_songs_in_db(update_configs, sp_inf: SpotifyInformation, db_inf: DatabaseInformation,
                       db_int: DatabaseInteraction, **kwargs):
    songset_played = sp_inf.get_last_played_tracks_since(util.previous_quarter())

    for config in update_configs:
        playlist = config.playlist
        songset_database = db_inf.get_songset_from_playlist(playlist.name)
        songset_spotify = sp_inf.get_songset_from_playlist(playlist)

        songset_known = songset_database - songset_spotify
        songset_left = songset_database - songset_known
        songset_unknown = songset_left - (songset_left - songset_played)

        db_int.update_known_songset(songset_known)
        db_int.update_unknown_songset(songset_unknown)


def update_tracks_in_spotify(db_inf, db_int, spotify_connection, **kwargs):
    action_dict = db_inf.get_songset_to_update_in_spotify()
    for action, playlist_dict in action_dict.items():
        for playlist, songset in playlist_dict.items():
            pl_int = PlaylistInteraction(spotify_connection, playlist)
            if action == 'delete':
                pl_int.remove_songset(songset)
            elif action == 'insert':
                pl_int.add_songset(songset)
            db_int.delete_from_song_playlist_update(songset, action)
6
if __name__ == "__main__":
    main()
