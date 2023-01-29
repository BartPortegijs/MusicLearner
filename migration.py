import pandas as pd
from database.connection import DatabaseConnection
from database.interaction import DatabaseInteraction
# from database.information import DatabaseInformation
from spotify.connection import connect_spotify_from_config
from spotify.information import SpotifyInformation

path_csv = 'H:\Mijn Drive\Spoti\migration_data.csv'
database = 'music_learner.db'
pd_csv = pd.read_csv(path_csv, index_col=0)

with DatabaseConnection('music_learner.db') as (curs, conn):
    db_int = DatabaseInteraction(curs, conn)
    spotify_connection = connect_spotify_from_config()
    sp_inf = SpotifyInformation(spotify_connection)

    for i, row in pd_csv.iterrows():
        track = sp_inf.get_track_from_spotify_id(row['spotify_id'])
        db_int.insert_single_track(track, row['learning_state_id'], None, row['next_date'])
        if i % 100 == 0:
            print(f'{i}/{len(pd_csv)}')
    db_int.commit()
