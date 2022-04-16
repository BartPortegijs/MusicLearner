from spotify_interaction import check_equality_songlist_playlist, get_playlist, songlist_from_playlist
from data import SongList, load_songlist_from_saves_directory
from util import date_from_today, datestring_to_date

def update_playlist(songlist_name, status):
    songlist = load_songlist_from_saves_directory(songlist_name)
    playlist = get_playlist(songlist.name)
    if not check_equality_songlist_playlist(songlist, playlist):
        print('songlists not equal')

    sample_size = get_number_of_songs_to_add(songlist)
    filtered_songlist = get_filtered_list_of_database_by_status(status)
    filtered_songlist = filter_by_date(filtered_songlist)
    filtered_songlist -= songlist_from_playlist(playlist)

    songlist_sample = filtered_songlist.sample(sample_size)

    playlist.add_songlist(songlist_sample)
    songlist += songlist_sample
    songlist.save_songlist()

def get_number_of_songs_to_add(songlist, max_number=25):
    return max(max_number - len(songlist), 0)

def get_filtered_list_of_database_by_status(status):
    songlist_database = load_songlist_from_saves_directory('database')

    if status == 'first_check':
        track_list = [track for track in songlist_database if track.learning_state.state == 'check' and track.learning_state.phase == 0]
    elif status == 'check':
        track_list = [track for track in songlist_database if track.learning_state.state == status and track.learning_state.phase >= 1]
    else:
        track_list = [track for track in songlist_database if track.learning_state.state == status]
    
    return SongList(status, track_list)

def filter_by_date(songlist):
    track_list = []
    today = datestring_to_date(date_from_today(0))

    for track in songlist:
        next_date = datestring_to_date(track.learning_state.next_date)
        if next_date <= today:
            track_list.append(track)
    return SongList(songlist.name, track_list)

if __name__ == "__main__":
    list_updatable_songlists = ['check_addition', 'known_addition', 'unknown_addition', 'first_check', 'check', 'learn', 'test']
    for songlist_name in list_updatable_songlists:
        update_playlist(songlist_name)