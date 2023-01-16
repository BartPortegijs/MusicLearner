PRAGMA foreign_keys = ON;

CREATE TABLE song (
    id integer PRIMARY KEY,
    title text NOT NULL,
    artists text NOT NULL,
    UNIQUE(title, artists)
);
CREATE INDEX spotify_song_title_idx ON song(title);
CREATE INDEX spotify_song_artists_idx ON song(artists);

CREATE TABLE track (
    id integer PRIMARY KEY,
    song_id integer NOT NULL,
    spotify_track_id text NOT NULL UNIQUE,
    active bool NOT NULL,
    FOREIGN KEY(song_id) REFERENCES song(id)
);
CREATE INDEX spotify_song_id_idx ON track(spotify_track_id);
CREATE INDEX song_id_idx ON track(song_id);

CREATE TABLE artist (
    id integer PRIMARY KEY,
    name text NOT NULL,
    spotify_artist_id text NOT NULL UNIQUE
);
CREATE INDEX spotify_spotify_artist_id_idx ON artist(spotify_artist_id);

CREATE TABLE song_artist (
    id integer PRIMARY KEY,
    song_id integer NOT NULL,
    artist_id integer NOT NULL,
    FOREIGN KEY(song_id) REFERENCES song(id),
    FOREIGN KEY(artist_id) REFERENCES artist(id),
    UNIQUE(song_id, artist_id)
);
CREATE INDEX song_artist_song_idx ON song_artist(song_id);
CREATE INDEX song_artist_artist_idx ON song_artist(artist_id);

CREATE TABLE learning_state (
    id integer PRIMARY KEY,
    phase integer NOT NULL,
    activity text NOT NULL CHECK (activity IN ('learn', 'check', 'test', 'first_check', 'finished')),
    next_id_positive integer,
    next_id_negative integer,
    days_before_active integer
);


CREATE TABLE song_state (
    id integer PRIMARY KEY,
    song_id integer NOT NULL,
    learning_state_id integer NOT NULL,
    song_in_playlist bool NOT NULL,
    next_date date,
    FOREIGN KEY(song_id) REFERENCES song(id),
    FOREIGN KEY(learning_state_id) REFERENCES learning_state(id)
);

CREATE INDEX song_state_learning_state_id_idx ON song_state(learning_state_id);
CREATE INDEX song_state_next_date_idx ON song_state(next_date);

CREATE TRIGGER song_state_insert AFTER INSERT ON song_state
BEGIN
    INSERT INTO song_state_history( song_id, learning_state_id, song_in_playlist, next_date,
                                    row_start, row_end, row_active)
    VALUES (new.song_id, new.learning_state_id, new.song_in_playlist, new.next_date,
                    DATETIME('now', 'localtime'), '2100-01-01 00:00:00', 1);
END;


CREATE TRIGGER song_state_update AFTER UPDATE ON song_state
BEGIN
    UPDATE song_state_history
    SET row_end = DATETIME('now', 'localtime'),
        row_active = 0
     WHERE  song_id = new.song_id
        AND row_active = 1;

    INSERT INTO song_state_history( song_id, learning_state_id, song_in_playlist, next_date,
                                    row_start, row_end, row_active)
    VALUES (new.song_id, new.learning_state_id, new.song_in_playlist, new.next_date,
                                    DATETIME('now', 'localtime'), '2100-01-01 00:00:00', 1);
END;

CREATE TABLE song_state_history (
    id integer PRIMARY KEY,
    song_id integer NOT NULL,
    learning_state_id integer NOT NULL,
    song_in_playlist bool NOT NULL,
    next_date date,
    row_start timestamp NOT NULL,
    row_end timestamp NOT NULL,
    row_active bool NOT NULL,
    FOREIGN KEY(song_id) REFERENCES song(id),
    FOREIGN KEY(learning_state_id) REFERENCES learning_state(id)
);

CREATE TABLE tag (
    id integer PRIMARY KEY,
    song_id integer NOT NULL,
    tag text NOT NULL,
    FOREIGN KEY(song_id) REFERENCES song(id)
);

CREATE TABLE song_playlist(
    id integer PRIMARY KEY,
    song_id integer NOT NULL,
    playlist_name integer NOT NULL,
    FOREIGN KEY(song_id) REFERENCES song(id),
    FOREIGN KEY(playlist_name) REFERENCES playlist(name)
);

CREATE TABLE song_playlist_update(
    id integer PRIMARY KEY,
    song_id integer NOT NULL,
    playlist_name integer NOT NULL,
    action integer NOT NULL,
    FOREIGN KEY(song_id) REFERENCES song(id),
    FOREIGN KEY(playlist_name) REFERENCES playlist(name)
);

-- Songs to add in spotify playlist
CREATE TRIGGER song_playlist_insert AFTER INSERT ON song_playlist
BEGIN
    INSERT INTO song_playlist_update(song_id, playlist_name, action)
    VALUES (new.song_id, new.playlist_name, 'insert');
END;

-- Songs to remove in spotify playlist
CREATE TRIGGER song_playlist_delete AFTER DELETE ON song_playlist
BEGIN
    INSERT INTO song_playlist_update(song_id, playlist_name, action)
    VALUES (old.song_id, old.playlist_name, 'delete');
END;

CREATE TABLE playlist(
    id integer PRIMARY KEY,
    name text NOT NULL UNIQUE,
    spotify_id text
);
CREATE INDEX playlist_name_idx ON playlist(name);

CREATE TABLE playlist_config(
    id integer PRIMARY KEY,
    playlist_id integer NOT NULL,
    config_type text NOT NULL,
    variable text,
    sign text,
    value text,
    FOREIGN KEY(playlist_id) REFERENCES playlist(id),
    CHECK (variable IN ('tag', 'artist', 'learning_state_id', 'activity', 'phase')),
    CHECK (config_type IN ('filter', 'max_nr_of_tracks', 'remove_when_zero', 'only_update_triggered',
                            'introduction_state', 'introduction_tag', 'remove', 'repeat', 'keep_unknown'))
);
CREATE INDEX playlist_config_playlist_id_idx ON playlist_config(playlist_id);


CREATE VIEW learning_information AS
WITH song_track AS
	(SELECT
		song.id AS song_id,
		song.title,
		song.artists,
		track.spotify_track_id,
		ROW_NUMBER() OVER (PARTITION BY song.title, track.spotify_track_id
			ORDER BY track.spotify_track_id) AS nr_spotify_id
	FROM song
	LEFT JOIN track
		ON song.id = track.song_id
	WHERE track.active = 1),
song_learn AS
	(SELECT
		song_track.song_id,
		song_track.title,
		song_track.artists,
		song_track.spotify_track_id,
		song_state.song_in_playlist,
		song_state.next_date,
		learning_state.id AS learning_id,
		learning_state.phase,
		learning_state.activity,
		learning_state.next_id_positive,
		learning_state.next_id_negative,
		learning_state.days_before_active,
		state_positive.days_before_active AS days_before_active_positive,
		state_negative.days_before_active AS days_before_active_negative
	FROM song_track
	LEFT JOIN song_state
		ON song_track.song_id = song_state.song_id
	LEFT JOIN learning_state
	    ON song_state.learning_state_id = learning_state.id
	LEFT JOIN learning_state AS state_positive
		ON learning_state.next_id_positive = state_positive.id
	LEFT JOIN learning_state AS state_negative
		ON learning_state.next_id_negative = state_negative.id
	WHERE song_track.nr_spotify_id = 1)
SELECT
	*
FROM song_learn;

CREATE VIEW track_information AS
WITH song_track AS
	(SELECT
		song.id AS song_id,
		song.title,
		song.artists,
		track.spotify_track_id,
		ROW_NUMBER() OVER (PARTITION BY song.title, track.spotify_track_id
			ORDER BY track.spotify_track_id) AS nr_spotify_id
	FROM song
	LEFT JOIN track
		ON song.id = track.song_id
	WHERE track.active = 1)
SELECT
	song_track.song_id,
	song_track.title,
	song_track.artists,
	song_track.spotify_track_id,
	artist.name,
	artist.spotify_artist_id
FROM song_track
LEFT JOIN song_artist
	ON song_track.song_id = song_artist.song_id
LEFT JOIN artist
	ON song_artist.artist_id = artist.id
WHERE song_track.nr_spotify_id = 1;

CREATE VIEW history_information AS
SELECT
    song.id AS song_id,
	song.title ,
	song.artists ,
	ssh.learning_state_id ,
	ssh.song_in_playlist,
	ssh.next_date,
	ssh.row_start ,
	ssh.row_end ,
	ssh.row_active
FROM song
LEFT JOIN song_state_history ssh
	ON song.id = ssh.song_id;

CREATE VIEW	tag_information AS
SELECT
	learning_information.*,
	tag.tag
FROM learning_information
LEFT JOIN tag
	ON learning_information.song_id = tag.song_id;

CREATE VIEW playlist_config_information AS
SELECT
    pl.id AS playlist_id,
    pl.name AS playlist_name,
    pl.spotify_id,
    pc.config_type,
    pc.variable,
    pc.sign,
    pc.value
FROM playlist_config pc
LEFT JOIN playlist pl
    ON pc.playlist_id = pl.id;

CREATE VIEW song_playlist_information AS
SELECT
    C.id AS song_id,
    C.title,
	C.artists,
    B.spotify_track_id,
    D.name AS playlist_name,
    D.spotify_id AS spotify_playlist_id
FROM playlist D
LEFT JOIN song_playlist A
    ON A.playlist_name = D.name
LEFT JOIN track B
    ON A.song_id = B.song_id
LEFT JOIN song C
    ON A.song_id = C.id;

CREATE VIEW song_playlist_update_information AS
SELECT
    C.id AS song_id,
    C.title,
	C.artists,
    B.spotify_track_id,
    D.name AS playlist_name,
    D.spotify_id AS spotify_playlist_id,
    A.action
FROM song_playlist_update A
LEFT JOIN track B
    ON A.song_id = B.song_id
LEFT JOIN song C
    ON A.song_id = C.id
LEFT JOIN playlist D
    ON A.playlist_name = D.name;
