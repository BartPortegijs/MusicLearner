import pickle
from random import sample
import os
import util

class SongList():
    def __init__(self, name, list_tracks):
        self.name = name
        self.list_tracks = list_tracks

    def __getitem__(self, i): return self.list_tracks[i]
    def __len__(self): return len(self.list_tracks)

    def __repr__(self):
        repr_string = f"{self.name}:\n"
        for i in range(len(self)):
            repr_string += f'{i}) {self[i]}\n'
        return repr_string

    def __contains__(self, item):
        for track in self:
            if item == track: return True
        return False

    def __sub__(self, songlist):
        list_tracks = [track for track in self if track not in songlist]
        return SongList(self.name,list_tracks)

    def __add__(self, addition):
        if type(addition) == Track:
            addition = [addition]
        if type(addition) == list:
            addition = SongList(None, addition)
        songlist_after_addition = self.addition_songlist(addition)
        return songlist_after_addition

    def addition_songlist(self, songlist):
        songlist_without_duplicates = songlist - self
        list_tracks = self.list_tracks + songlist_without_duplicates.list_tracks
        return SongList(self.name,list_tracks)

    def save_songlist(self):
        file_path = f"saves/{self.name}.obj" 
        with open(file_path, 'wb') as f:
            pickle.dump(self, f)

    def sample(self, size):
        size = min(size, len(self.list_tracks))
        list_tracks = sample(self.list_tracks, size)
        return SongList(f"{self.name}_sample", list_tracks)

    def update(self, songlist):
        for i in range(len(self)):
            if self[i] in songlist:
                idx = songlist.list_tracks.index(self[i])
                self.list_tracks[i] = songlist[idx]

def load_or_create_and_load_songlist(file_name):
    path = f'saves/{file_name}.obj'
    if not os.path.exists(path):
        save_empty_songlist(file_name)
    return load_songlist(path)

def load_songlist_from_saves_directory(file_name):
    path = f'saves/{file_name}.obj'
    return load_songlist(path)

def load_songlist(path):
    with open(path, 'rb') as f:
        songlist = pickle.load(f)
        return songlist

def save_empty_songlist(name):
    songlist = SongList(name, [])
    songlist.save_songlist()
    return 

class Track():
    timedelta_dict = {1: 0, 2:7, 3: 20, 4: 60, 5:180, 0:None}

    def __init__(self, dict):
        self.dict = dict
        self.learning_state = LearningState()
    
    def get_artists(self):
        artist_list = [{"artist":artist['name'],"artist_id":artist['id'] } for artist in self['artists']]
        return ", ".join([artist_dict['artist'] for artist_dict in artist_list])

    def get_title(self):
        return self['name'].partition(" - ")[0]

    def get_dutch_market(self):
        return 'NL' in self['available_markets']

    def __repr__(self):
        return f"{self.get_title()} - {self.get_artists()}"

    def __eq__(self, other):
        return self.__repr__().lower() == other.__repr__().lower()

    def __ge__(self, other):
        return self.__repr__().lower() >= other.__repr__().lower()

    def __le__(self, other):
        return self.__repr__().lower() <= other.__repr__().lower()

    def __gt__(self, other):
        return self.__repr__().lower() > other.__repr__().lower()

    def __lt__(self, other):
        return self.__repr__().lower() < other.__repr__().lower()

    def __getitem__(self, key):
        return self.dict[key]

    def update_track(self, result_known: bool):
        self.learning_state.update_state(result_known)

    def update_track_learning_state_key(self, key):
        self.learning_state.set_state_attributes(key)

class LearningState():
    timedelta_dict = {1: 1, 2:7, 3: 20, 4: 60, 5:180, 0:None}
    states_dict = {
        0: ('check', 0, 99, 2),     99: ('finished', 0, 99, 99),
        1: ('check', 1, 4, 2),      2: ('learn', 1, 3, 2),      3: ('test', 1, 1, 2),
        4: ('check', 2, 7, 5),      5: ('learn', 2, 6, 5),      6: ('test', 2, 4, 1),
        7: ('check', 3, 10, 8),     8: ('learn', 3, 9, 8),      9: ('test', 3, 7, 4),
        10: ('check', 4, 13, 11),   11: ('learn', 4, 12, 11),   12: ('test', 4, 10, 7),
        13: ('check', 5, 99, 14),   14: ('learn', 5, 15, 14),   15: ('test', 5, 13, 10),           
    } 

    def __init__(self, state_atttribute_key = 0):
        self.next_date = util.date_from_today(0) 
        self.prev_date = None
        self.set_state_attributes(state_atttribute_key)

    def set_state_attributes(self, states_dict_lookup_number):
        self.state, self.phase, self.next_lookup_number_positive, self.next_lookup_number_negative = self.states_dict[states_dict_lookup_number]

    def __repr__(self):
        representation = f"""State: {self.state}\nPhase: {self.phase}\nPrevious date: {self.prev_date}\nNext date: {self.next_date}"""
        return representation
    
    def update_state(self, known_song: bool):
        if known_song:
            if self.state in ['check', 'test']: 
                self.prev_date = util.date_from_today(0)
            self.set_state_attributes(self.next_lookup_number_positive)
        else:
            self.set_state_attributes(self.next_lookup_number_negative)
        
        if self.state in ['check']:
            self.next_date = util.date_from_today(self.timedelta_dict[self.phase])  
        if self.state in ['test']:
            self.next_date = util.date_from_today(1)          
        return


