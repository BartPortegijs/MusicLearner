import util
from database.connection import DatabaseConnection
from database.information import DatabaseInformation
from database.interaction import DatabaseInteraction
from spotify.connection import connect_spotify_from_config
from spotify.interaction import PlaylistInteraction
from spotify.information import SpotifyInformation
import data_classes

import logging


def main():
    logging.info('Started at ')
    with DatabaseConnection('music_learner.db') as (curs, conn):
        try:
            # Create all classes for connection with database and spotify
            db_inf = DatabaseInformation(curs)
            db_int = DatabaseInteraction(curs, conn)
            spotify_connection = connect_spotify_from_config()
            sp_inf = SpotifyInformation(spotify_connection)
            connection_classes = {'spotify_connection': spotify_connection, 'sp_inf': sp_inf,
                                  'db_inf': db_inf, 'db_int': db_int}

            # Playlist initiation
            create_playlists_from_database(**connection_classes)
            remove_configs, repeat_configs, insert_configs, update_configs = split_playlist_types(**connection_classes)

            insert_new_songs_to_db(insert_configs, **connection_classes)
            remove_songs_from_db(remove_configs, **connection_classes)
            repeat_songs_from_db(repeat_configs, **connection_classes)
            update_songs_in_db(update_configs, **connection_classes)
            conn.commit()

            db_int.insert_songs_in_playlist_db(update_configs)
            update_tracks_in_spotify(**connection_classes)
            conn.commit()

            # add_information_empty_song(db_inf, db_int, sp_inf)
            # conn.commit()

            check_consistency(update_configs, **connection_classes)
        except:
            logging.exception('There is an error')

    logging.info('Finished!')


def create_playlists_from_database(spotify_connection, db_inf, db_int, sp_inf, **kwargs):
    """Create the playlists in Spotify as defined in the database."""
    spotify_playlists = None
    for playlist in db_inf.get_playlists():

        # Checks if database has spotify_id, and otherwise add spotify_id for existing spotify playlists
        if playlist.spotify_id is None:
            if spotify_playlists is None:
                spotify_playlists = sp_inf.get_relevant_playlists()
            playlist = sp_inf.get_playlist_from_playlist(playlist, playlist_list=spotify_playlists)
            if playlist.spotify_id is not None:
                db_int.update_playlist(playlist)
                logging.info(f'Updated spotify_id in database for playlist {playlist}')
            # If after previous check, there is still no spotify_id, we should create playlist in spotify.
            else:
                sp_int = PlaylistInteraction(spotify_connection, playlist)
                playlist_spotify = sp_int.create_playlist(spotify_connection, playlist)
                logging.info(f'Created Spotify playlist {playlist_spotify.playlist}')
                db_int.update_playlist(playlist_spotify.playlist)
                logging.info(f'Updated spotify_id in database for playlist {playlist_spotify.playlist}')
    if spotify_playlists is None:
        logging.info('No update on playlist information')


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
    logging.info(f'''Selected type of playlists: \n\t\tRemove: {remove_configs}\n\t\tRepeat: {repeat_configs}\n\t\t\
Insert: {insert_configs}\n\t\tUpdate: {update_configs}''')
    return remove_configs, repeat_configs, insert_configs, update_configs


def _structure_song_action(config: data_classes.PlaylistConfig, sp_inf: SpotifyInformation, db_int: DatabaseInteraction,
                           action: str, **kwargs):
    songset = sp_inf.get_songset_from_playlist(config.playlist)
    if len(songset) > 0:
        pl_int = PlaylistInteraction(sp_inf.conn, config.playlist)
        if action == 'insert':
            state = config.introduction_state
            tag = config.introduction_tag
            db_int.insert_songset(songset, next_state=state, tag=tag)
            logging.info(f'Added songset to database with introduction state {state} and tag {tag}: \n{songset}')
        if action == 'remove':
            db_int.remove_songset(songset)
            logging.info(f'Removed songset from database: \n{songset}')
        if action == 'repeat':
            db_int.update_repeat_songset(songset)
            logging.info(f'Repeat songset from database: \n{songset}')
        pl_int.remove_songset(songset)
    else:
        logging.info(f'Playlist {config.playlist.name} is empty. No update done.')
    return songset


def insert_new_songs_to_db(insert_configs: list, **kwargs):
    for config in insert_configs:
        _structure_song_action(config, action='insert', **kwargs)


def remove_songs_from_db(remove_configs: list, **kwargs):
    for config in remove_configs:
        _structure_song_action(config, action='remove', **kwargs)


def repeat_songs_from_db(repeat_configs: list, **kwargs):
    for config in repeat_configs:
        _structure_song_action(config, action='repeat', **kwargs)


def update_songs_in_db(update_configs, sp_inf: SpotifyInformation, db_inf: DatabaseInformation,
                       db_int: DatabaseInteraction, **kwargs):
    songset_played = sp_inf.get_last_played_tracks_since(util.previous_quarter())
    for config in update_configs:
        playlist = config.playlist
        songset_database = db_inf.get_songset_from_playlist(playlist.name)
        if len(songset_database) == 0:
            logging.info(f'Empty songset for playlist {config.name} in database')
            continue

        songset_spotify = sp_inf.get_songset_from_playlist(playlist)

        songset_known = songset_database - songset_spotify
        if len(songset_known) > 0:
            db_int.update_known_songset(songset_known)
            logging.info(f'Update known songset for playlist {config.name}:\n{songset_known}')
        else:
            logging.info(f'No known update for playlist {config.name}')

        if not config.learn:
            if len(songset_played) > 0:

                songset_left = songset_database - songset_known
                songset_unknown = songset_left.intersection(songset_played)

                if len(songset_unknown) > 0:
                    db_int.update_unknown_songset(songset_unknown)
                    logging.info(f'Update unknown songset for playlist {config.name}:\n{songset_unknown}')
                else:
                    logging.info(f'No unknown update for playlist {config.name}')
            else:
                logging.info(f'No unknown update for playlist {config.name}')


def update_tracks_in_spotify(db_inf, db_int, spotify_connection, **kwargs):
    action_dict = db_inf.get_songset_to_update_in_spotify()
    for action, playlist_dict in action_dict.items():
        for playlist, songset in playlist_dict.items():
            pl_int = PlaylistInteraction(spotify_connection, playlist)
            if action == 'delete':
                pl_int.remove_songset(songset)
                logging.info(f'Removed songset from playlist {pl_int.playlist.name}:\n{songset}')
            elif action == 'insert':
                pl_int.add_songset(songset)
                logging.info(f'Inserted songset in playlist {pl_int.playlist.name}:\n{songset}')
            db_int.delete_from_song_playlist_update(songset, action)
            logging.info('Removed songset from database update table.')


def add_information_empty_song(db_inf, db_int, sp_inf):
    select_script = """SELECT title, artists FROM song LEFT JOIN track ON song.id = track.song_id WHERE 
                    track.song_id IS NULL """
    result = db_inf.query_to_list_dict(select_script)
    for row in result:
        songset_search = sp_inf.get_songset_from_search_query(f"{row['title']} {row['artists']}", limit=1)
        db_int.insert_songset(songset_search, next_state=0)


def check_consistency(update_configs, db_inf: DatabaseInformation, sp_inf: SpotifyInformation, **kwargs):
    configs_names = [config.name for config in update_configs]
    database_numbers = {k: v for k, v in db_inf.get_track_number_in_playlists().items() if k in configs_names}

    for config in update_configs:
        songset_spotify = sp_inf.get_songset_from_playlist(config.playlist)
        name = config.name
        db_num = database_numbers[name]['number']
        if db_num != len(songset_spotify):
            logging.warning(f"For playlist {name}: Database = {db_num}, Spotify = {len(songset_spotify)}")

    # Outer Join not supported by sqlite3. So, these test is remove for the time being.
    # query_1 = """SELECT * FROM
    #                 (SELECT
    #                     *
    #                 FROM song_state ss
    #                 WHERE ss.song_in_playlist = 1) A
    #                 FULL JOIN song_playlist B
    #                     ON A.song_id = B.song_id
    #                 WHERE A.id IS NULL OR B.id IS NULL"""
    #
    # if len(db_inf.query_to_list_dict(query_1)) != 0:
    #     logging.warning(f"Database song_playlist not consistent with song_state")


if __name__ == "__main__":
    logging.basicConfig(filename='log.log', encoding='utf-8', level=logging.INFO, format='%(asctime)s %(message)s',
                        datefmt='%d/%m/%Y %I:%M:%S %p')
    main()
