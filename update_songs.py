from spotify_interaction import get_last_played_tracks_since, songlist_from_playlist, get_playlist, check_equality_songlist_playlist_by_name
from data import load_songlist_from_saves_directory, SongList 
import time


def update_songs_in_database_from_songlist(name):
    songlist_database = load_songlist_from_saves_directory('database')
    songlist = load_songlist_from_saves_directory(name)

    known_songs, unknown_songs = get_known_unknown_songs_from_songlist(songlist)
    
    update_songlist(songlist_database, known_songs, unknown_songs)
    songlist_database.save_songlist()
    
    remove_songs_from_playlist(songlist.name, known_songs, unknown_songs)

    songlist = (songlist - known_songs) - unknown_songs
    songlist.save_songlist()

def get_known_unknown_songs_from_songlist(songlist, since = None):
    if not since: since = int(time.time()-4500)

    playlist_new = get_playlist(songlist.name)
    songlist_new = songlist_from_playlist(playlist_new)
    songlist_last_played = get_last_played_tracks_since(since)
    
    known_songs = songlist - songlist_new
    unknown_songs = songlist_new - (songlist_new - songlist_last_played)
    if songlist.name == 'learn':
        unknown_songs = SongList('unknown', [])
    
    return known_songs, unknown_songs

def update_songlist(songlist, known_songs, unknown_songs):
    update_songlist_by_known_songlist(songlist, known_songs)
    update_songlist_by_unknown_songlist(songlist, unknown_songs)

def update_songlist_by_known_songlist(songlist, known_songlist):
    for track in songlist:
        if track in known_songlist:
            track.update_track(result_known=True)

def update_songlist_by_unknown_songlist(songlist, unknown_songlist):
    for track in songlist:
        if track in unknown_songlist:
            track.update_track(result_known=False)

def remove_songs_from_playlist(name, known_songs, unknown_songs):
    playlist = get_playlist(name)
    playlist.remove_songlist(known_songs)
    playlist.remove_songlist(unknown_songs)