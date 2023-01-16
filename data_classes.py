from __future__ import annotations
from dataclasses import dataclass
from random import sample
from typing import Union


##################################################################################################################
@dataclass
class Track:
    artist: str
    title: str
    artist_tuple: tuple
    spotify_id: str
    played_at: str = None
    context: str = None

    @property
    def title_artist(self):
        return f"{self.title} - {self.artist}"

    def __repr__(self):
        return self.title_artist

    def __eq__(self, other: Track):
        return self.__repr__().lower() == other.__repr__().lower()

    def __hash__(self):
        return hash(self.title_artist)

    @classmethod
    def from_spotify_track_dict(cls, spotify_track_dict: dict) -> Track:
        track_dict = _TrackDict(spotify_track_dict=spotify_track_dict)
        return cls._from_track_dict(track_dict=track_dict)

    @classmethod
    def _from_track_dict(cls, track_dict: _TrackDict) -> Track:
        return cls(artist=track_dict.get_artists(), title=track_dict.get_title(),
                   artist_tuple=track_dict.get_artist_tuple(),
                   spotify_id=track_dict.get_spotify_id(), played_at=track_dict.get_played_at(),
                   context=track_dict.get_context())

    @classmethod
    def from_spotify_played_track_dict(cls, spotify_track_dict: dict) -> Track:
        spotify_track_dict['track']['played_at'] = spotify_track_dict['played_at']
        return cls.from_spotify_track_dict(spotify_track_dict['track'])

    @classmethod
    def from_spotify_playlist_track_dict(cls, spotify_playlist_track_dict: dict) -> Track:
        return cls.from_spotify_track_dict(spotify_playlist_track_dict['track'])


class _TrackDict:
    def __init__(self, spotify_track_dict: dict):
        self.track_dict = spotify_track_dict

    def __getitem__(self, key):
        return self.track_dict.get(key)

    def __repr__(self):
        return f'{self.track_dict}'

    def get_artists(self):
        return ", ".join([artist.name for artist in self.get_artist_tuple()])

    def get_artist_tuple(self):
        return tuple(Artist.from_spotify_artist_dict(artist_dict) for artist_dict in self['artists'])

    def get_title(self):
        return self['name'].partition(" - ")[0]

    def get_spotify_id(self):
        return self['id']

    def get_played_at(self):
        return self['played_at']

    def get_context(self):
        return self['context']


##################################################################################################################
@dataclass(frozen=True, eq=True)
class Artist:
    name: str
    spotify_id: str

    def __repr__(self):
        return f"{self.name}"

    @classmethod
    def from_spotify_artist_dict(cls, spotify_artist_dict):
        artist_dict = _ArtistDict(spotify_artist_dict)
        return cls._from_artist_dict(artist_dict)

    @classmethod
    def _from_artist_dict(cls, artist_dict):
        return cls(artist_dict.get_name(), artist_dict.get_spotify_id())


class _ArtistDict:
    def __init__(self, spotify_artist_dict):
        self.artist_dict = spotify_artist_dict

    def __getitem__(self, key):
        return self.artist_dict.get(key)

    def get_name(self):
        return self['name']

    def get_spotify_id(self):
        return self['id']

    def __repr__(self):
        return f'{self.artist_dict}'


##################################################################################################################
@dataclass
class SongSet:
    track_set: set[Track]

    # def __post_init__(self):
    #     assert type(self.track_set) == set

    def __getitem__(self, i):
        return tuple(self.track_set)[i]

    def __len__(self):
        return len(self.track_set)

    def __repr__(self):
        repr_string = ""
        for i in range(len(self)):
            repr_string += f'{i}) {self[i]}\n'
        return repr_string

    def __contains__(self, track):
        return track in self.track_set

    def __sub__(self, songset):
        return SongSet(self.track_set - songset.track_set)

    def __eq__(self, songset):
        return self.track_set == songset.track_set

    def get_track_ids(self):
        return [track.spotify_id for track in self.track_set]

    def get_track_ids_as_dict(self):
        return ({'spotify_id': track.spotify_id} for track in self.track_set)

    def extend(self, songs: Union[SongSet, Track]):
        if type(songs) == SongSet:
            assert type(songs.track_set) == set, f'{songs.track_set}'
            assert type(self.track_set) == set, f'{type(self.track_set)}, {self.track_set}'
            self.track_set.update(songs.track_set)
        if type(songs) == Track:
            self.track_set.update({songs})

    def sample(self, size):
        size = min(size, len(self))
        track_tuple = tuple(self.track_set)
        sample_tuple = sample(track_tuple, size)
        return SongSet(set(sample_tuple))


##################################################################################################################
@dataclass
class LearningState:
    id: int
    phase: int
    activity: str
    next_id_positive: int
    next_id_negative: int
    days_before_active: int


##################################################################################################################
class _PlaylistDict:
    def __init__(self, spotify_playlist_dict):
        self.playlist_dict = spotify_playlist_dict

    def __getitem__(self, key):
        return self.playlist_dict[key]

    def __repr__(self):
        return f'{self.playlist_dict}'

    def get_spotify_id(self):
        return self['id']

    def get_name(self):
        return self['name']


@dataclass
class Playlist:
    name: str
    spotify_id: str = None

    def __repr__(self):
        return f"""Playlist with name '{self.name}' and Spotify id '{self.spotify_id}'"""

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other: Playlist):
        return self.name == other.name

    @classmethod
    def from_spotify_playlist_dict(cls, spotify_playlist_dict: dict):
        playlist_dict = _PlaylistDict(spotify_playlist_dict)
        return cls._from_playlist_dict(playlist_dict)

    @classmethod
    def _from_playlist_dict(cls, playlist_dict: _PlaylistDict):
        return cls(spotify_id=playlist_dict.get_spotify_id(), name=playlist_dict.get_name())


@dataclass
class ConfigRule:
    """Describes the different rules for playlists behavior. As config type can be chosen:
    filter: Possible filers to select numbers for the playlist.
        As variables can be used as rows of the learning_information view in the database and the tag variable.
    max_nr_of_tracks: The maximum number of tracks in the database.
    Not implemented yet: remove_when_zero: The playlist will be removed when all songs are gone from the playlist
    Not implemented yet: only_update_triggered:
    introduction_state: When a song is added to this playlist, it gets added to the database with this state.
    introduction_tag: When a song is added to this playlist, it gets added with this tag.
    remove: When a song is added to this playlist, its spotify id is set to inactive in the database.
    repeat: When a song is added to this playlist, it will pop up in one of the playlists after some time.
    keep_unknown: If a song is seen as unknown, nothing is done with it."""
    config_type: str
    variable: str = None
    sign: str = None
    value: Union[str, int, bool] = None

    def __post_init__(self):
        assert self.config_type in ('filter', 'max_nr_of_tracks', 'remove_when_zero', 'only_update_triggered',
                                    'introduction_state', 'introduction_tag', 'remove', 'repeat', 'keep_unknown'), \
            f'Config type {self.config_type} is incorrect.'
        if self.config_type in ('max_nr_of_tracks', 'introduction_state'):
            self.value = int(self.value)
        if self.config_type in ('remove_when_zero', 'only_update_triggered', 'remove', 'repeat', 'keep_unknown'):
            self.value = bool(self.value)
        if self.config_type == 'filter':
            if self.variable in ('song_id', 'learning_id', 'phase', 'next_id_positive', 'next_id_negative', 'days_before_active',
                                 'days_before_active_positive', 'days_before_active_negative'):
                self.value = int(self.value)


@dataclass
class PlaylistConfig:
    playlist: Playlist
    rules: list[ConfigRule] = None

    def __post_init__(self):
        if self.remove is not None:
            assert self.filters is None
        if self.remove is not None:
            assert self.introduction_state is None

    @property
    def filters(self):
        return self.get_rules_list('filter')

    @property
    def max_nr_of_tracks(self):
        return self.get_value('max_nr_of_tracks')

    @property
    def remove_when_zero(self):
        return self.get_value('remove_when_zero')

    @property
    def only_update_triggered(self):
        return self.get_value('only_update_triggered')

    @property
    def introduction_state(self):
        return self.get_value('introduction_state')

    @property
    def introduction_tag(self):
        return self.get_value('introduction_tag')

    @property
    def remove(self):
        return self.get_value('remove')

    @property
    def repeat(self):
        return self.get_value('repeat')

    @property
    def keep_unknown(self):
        return self.get_value('keep_unknown')

    @property
    def spotify_id(self):
        return self.playlist.spotify_id

    @property
    def name(self):
        return self.playlist.name

    def get_value(self, rule_type):
        rules_list = self.get_rules_list(rule_type)
        if rules_list is None:
            return None
        assert len(rules_list) == 1, 'Function is not for multiple rule selection.'
        return rules_list[0].value

    def get_rules_list(self, config_type):
        rules_list = [rule for rule in self.rules if rule.config_type == config_type]
        if len(rules_list) == 0:
            return None
        return rules_list

    # def create_filter_query(self, limit=None):
    #     assert self.filters is not None
    #     insert_query = "INSERT INTO song_playlist(song_id, playlist_name) "
    #     start_query = f"SELECT song_id, '{self.playlist.name}' FROM {self._get_source_table()} WHERE "
    #     where_query, insert_values = self._get_where_statement()
    #
    #     except_query = f" EXCEPT SELECT song_id, playlist_name FROM song_playlist_information"
    #
    #     query = insert_query + start_query + where_query + except_query
    #     if limit is not None:
    #         limit_query = " LIMIT ?"
    #         insert_values.append(limit)
    #         query += limit_query
    #
    #     return query, insert_values

    def create_filter_select_query(self, limit=None):
        assert self.filters is not None
        start_query = f"SELECT song_id, '{self.playlist.name}' AS playlist_name FROM {self._get_source_table()} WHERE "
        where_query, insert_dict = self._get_where_statement()

        except_query = f" EXCEPT SELECT song_id, playlist_name FROM song_playlist_information"

        query = start_query + where_query + except_query
        if limit is not None:
            limit_query = " LIMIT :limit"
            insert_dict['limit'] = limit
            query += limit_query

        return query, insert_dict

    def _get_source_table(self):
        for row in self.filters:
            if row.variable == 'tag':
                return 'tag_information'
        return 'learning_information'

    def _get_where_statement(self):
        insert_dict = dict()
        where_query = "next_date <= DATE('now')"
        for i, row in enumerate(self.filters):
            insert_name = f'value_{i}'
            if row.variable == 'phase':
                row.value = int(row.value)
            where_query += f" AND {row.variable} {row.sign} :{insert_name}"
            insert_dict[insert_name] = row.value
        return where_query, insert_dict


