import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config import read_config, config_path
import util
from data import Track, SongList, load_songlist_from_saves_directory

def connect_spotify_from_config(config_path):
    conn_dict = read_config(config_path)
    return connect_spotify(**conn_dict)

def connect_spotify(client_id,secret_id,scope,uri, **kwargs):
    auth_manager=SpotifyOAuth(client_id=client_id, client_secret=secret_id, redirect_uri=uri ,scope=scope, requests_session=True)
    return spotipy.Spotify(auth_manager=auth_manager)

def get_all_playlists():
    playlist_iterator = PlaylistIterator()
    playlist_list = playlist_iterator.transform_items_to_class()

    while playlist_iterator['next']:
        next(playlist_iterator)
        playlist_list.extend(playlist_iterator.transform_items_to_class())
    return playlist_list

def get_playlist(name):
    playlist_iterator = PlaylistIterator()
    playlist = playlist_iterator.get_item(name)
    
    while playlist_iterator['next'] and playlist is None:
        next(playlist_iterator)
        playlist = playlist_iterator.get_item(name)
    return playlist

def search_tracks(query, limit = 10):
    max_iteration_step = min(limit, 50)
    limit -= max_iteration_step

    search_iterator = SearchTrackIterator(query= query, limit=max_iteration_step)
    search_list = search_iterator.transform_items_to_class()
    while search_iterator['next'] and limit>0:
        max_iteration_step = min(limit, 50)
        limit -= max_iteration_step

        next(search_iterator)
        search_list.extend(search_iterator.transform_items_to_class()[0:max_iteration_step])

    return SongList(query, search_list)

def get_last_played_tracks_since(timestamp):
    songlist_last_played = get_last_played_tracks()
    if timestamp is None:
        return songlist_last_played
    else:
        track_list = [track for track in songlist_last_played if compare_timestamps(track['played_at'], timestamp)]
        return SongList('last_played', track_list)

def get_last_played_tracks():
    played_iterator = PlayedTrackIterator()
    played_list = played_iterator.transform_items_to_class()
    return SongList('last_played', played_list)

def compare_timestamps(timestamp_milliseconds, timestamp):
    if type(timestamp_milliseconds) == str: timestamp_milliseconds = util.timestampstring_to_timestamp_milliseconds(timestamp_milliseconds)
    if type(timestamp) == str: timestamp = util.timestampstring_to_timestamp(timestamp)
    return timestamp_milliseconds > timestamp

class Iterator():
    def __init__(self, *args, **kwargs):
        self.sp = connect_spotify_from_config(config_path)
        self.iterator = self.get_iterator(*args, **kwargs)
        self.item_class = self.get_item_class()

    def get_iterator(self, *args, **kwargs):
        raise NotImplementedError

    def get_item_class(self):
        raise NotImplementedError

    def transform_items_to_class(self):
        return [self.item_class(dict) for dict in self['items']]

    def get_item(self, name):
        for dict in self['items']:
            if dict['name']==name:
                return self.item_class(dict)

    def __getitem__(self, key): 
        return self.iterator[key]

    def __next__(self):
        self.iterator = self.sp.next(self.iterator)  

class PlaylistIterator(Iterator):
    def get_iterator(self):
        return self.sp.current_user_playlists()    

    def get_item_class(self):
        return Playlist

class TrackIterator(Iterator):
    def get_item_class(self):
        return Track

    def get_iterator(self, *args, **kwargs):
        raise NotImplementedError

class SearchTrackIterator(TrackIterator):
    def get_iterator(self, query, limit):
        return self.sp.search(query, limit)['tracks']

    def __next__(self):
        self.iterator = self.sp.next(self.iterator)['tracks']  

class PlayedTrackIterator(TrackIterator):
    def get_iterator(self):
        return self.sp.current_user_recently_played()      

    def transform_items_to_class(self):
        track_list = []
        for dict in self['items']:
            copy_played_at_to_track_dict_level(dict)
            track_list.append(self.item_class(dict['track']))
        return track_list

    def __next__(self):
        NotImplementedError 

class PlaylistTrackIterator(TrackIterator):
    def get_iterator(self, playlist_id):
        return self.sp.playlist_items(playlist_id)

    def __next__(self):
        self.iterator = self.sp.next(self.iterator) 

    def transform_items_to_class(self):
        return [self.item_class(dict['track']) for dict in self['items']]

def copy_played_at_to_track_dict_level(dict):
    dict['track']['played_at'] = dict['played_at']

def songlist_from_playlist(playlist):
    track_list = tracklist_from_playlist(playlist['id'])
    return SongList(playlist['name'], track_list)

def tracklist_from_playlist(playlist_id):
    result_iterator = PlaylistTrackIterator(playlist_id)
    track_list = result_iterator.transform_items_to_class()

    while result_iterator['next']:
        next(result_iterator)
        track_list.extend(result_iterator.transform_items_to_class())
    return track_list

class Playlist():
    "Class with methods for playlist"
    def __init__(self, dict):
        self.sp = connect_spotify_from_config(config_path)
        self.dict = dict
        assert self.dict['id'] is not None

    def __getitem__(self, key):
        return self.dict[key]

    def __repr__(self): 
        return f"Playlist with name '{self['name']}'"      

    def delete(self):
        self.sp.current_user_unfollow_playlist(self['id'])

    def add_songlist(self, songlist):
        self.add_tracks(songlist.list_tracks)

    def add_tracks(self, track_list):
        self.add_track_ids([track['id'] for track in track_list])

    def add_track_ids(self, track_id_list):
        "Adds a list of track by track_ids to playlist"
        for track_ids_chunk in util.split_into_chunks(track_id_list,100):  
            self.sp.playlist_add_items(self['id'], track_ids_chunk)
        return

    def remove_songlist(self, songlist):
        self.remove_tracks(songlist.list_tracks)

    def remove_tracks(self, track_list):
        self.remove_track_ids([track['id'] for track in track_list])

    def remove_track_ids(self, track_id_list):
        "Removes track with track_id from playlist"
        for track_ids_chunk in util.split_into_chunks(track_id_list,100):  
            self.sp.playlist_remove_all_occurrences_of_items(self['id'], track_ids_chunk)
        return

    def clear(self):
        self.remove_track_ids([track['id'] for track in tracklist_from_playlist(self['id'])])

def clear_playlist(name):
    playlist_instance = get_playlist(name)
    playlist_instance.clear()

def create_or_and_get_playlist(name):
    playlist_instance = get_playlist(name)
    if playlist_instance is None: 
        create_playlist(name)
        playlist_instance = get_playlist(name)

def create_playlist(name):
    sp = connect_spotify_from_config(config_path)
    user_id = sp.me()['id']
    sp.user_playlist_create(user_id,name,public='False')

def create_playlist_from_songlist(songlist):
    create_playlist(songlist.name)
    playlist_instance = get_playlist(songlist.name)
    playlist_instance.add_songlist(songlist)

def get_track_from_id(track_id):
    sp = connect_spotify_from_config(config_path)
    track_dict = sp.track(track_id)
    return Track(track_dict)

def check_equality_songlist_playlist_by_name(name):
    songlist = load_songlist_from_saves_directory(name)
    playlist = get_playlist(name)
    return check_equality_songlist_playlist(songlist, playlist)

def check_equality_songlist_playlist(songlist, playlist):
    songlist2 = songlist_from_playlist(playlist)
    return check_equality_songlists(songlist, songlist2)

def check_equality_songlists(songlist1, songlist2):
    if len(songlist1) != len(songlist2):
        return False

    songlist1, songlist2 = map(sorted, (songlist1, songlist2))
    for i in range(len(songlist1)):
        if songlist1[i] != songlist2[i]:
            return False
    return True
    

    