import os
from data import save_empty_songlist
from spotify_interaction import create_playlist

addition_name_list = ['check_addition', 'known_addition', 'unknown_addition']
playlist_name_list = ['check', 'learn', 'test', 'first_check']

def startup(playlist_name_list):
    if not os.path.exists('saves'): os.makedirs('saves')

    for playlist_name in playlist_name_list:
        if not os.path.exists(f'saves/{playlist_name}.obj'):
            create_playlist(playlist_name)
            save_empty_songlist(playlist_name)
    if not os.path.exists(f'saves/database.obj'):
        save_empty_songlist('database')

if __name__ == "__main__":
    startup(addition_name_list +playlist_name_list)