from spotify_interaction import get_playlist, songlist_from_playlist, clear_playlist
from data import load_songlist_from_saves_directory  
from util import date_from_today

playlist_lookup = {'check_addition': 0, 'known_addition': 99, 'unknown_addition': 2}
playlist_next_date = {'check_addition': 0, 'known_addition': None, 'unknown_addition': 0}

def add_new_songs_to_database():
    songlist_database = load_songlist_from_saves_directory('database')
    for key in playlist_lookup:
        playlist = get_playlist(key)
        songlist_addition = songlist_from_playlist(playlist)
        for track in songlist_addition:
            lookup = playlist_lookup[key]
            days_from_today = playlist_next_date[key]

            track.update_track_learning_state_key(lookup)
            if days_from_today is not None:
                track.learning_state.next_date = date_from_today(days_from_today)

        if len(songlist_addition) > 0:
            songlist_database += songlist_addition
            songlist_database.save_songlist()

        clear_playlist(key)

def remove_songs_from_database():
    playlist = get_playlist('remove_list')
    songlist_remove = songlist_from_playlist(playlist)
    if len(songlist_remove)>0:
        songlist_database = load_songlist_from_saves_directory('database')
        songlist_database.list_tracks = [track for track in songlist_database if track not in songlist_remove]
        songlist_database.save_songlist()
    clear_playlist('remove_list')

if __name__ == "__main__":
    add_new_songs_to_database()

