from startup import startup, addition_name_list, playlist_name_list
from add_tracks import add_new_songs_to_database, remove_songs_from_database
from update_songs import update_songs_in_database_from_songlist, check_equality_songlist_playlist_by_name
from update_playlists import update_playlist

if __name__ == "__main__":
    startup(addition_name_list +playlist_name_list)
    add_new_songs_to_database()
    remove_songs_from_database()

    for songlist_name in playlist_name_list:
        update_songs_in_database_from_songlist(songlist_name)
        check_equality_songlist_playlist_by_name(songlist_name)

    for songlist_name in playlist_name_list:
        status = songlist_name
        update_playlist(songlist_name, status)