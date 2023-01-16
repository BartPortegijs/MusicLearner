from data_classes import *
import util

database_tables = {'song', 'artist', 'song_artist', 'tag', 'track', 'learning_state', 'song_state',
                   'song_state_history', 'song_playlist', 'song_playlist_update', 'playlist', 'playlist_config'}
database_views = {'learning_information', 'track_information', 'history_information', 'tag_information',
                  'song_playlist_information', 'playlist_config_information', 'song_playlist_update_information'}

# Song with multiple artists
title_multiple = 'HUTS'
spotify_id_multiple = '0UMaqPntFC8dFOc7p3Iefj'
artist_multiple = 'The Blockparty, Esko, Mouad Locos, JoeyAK, Young Ellens, Chivv'
artist_tuple_multiple = (Artist('The Blockparty', '1zmmIiBBODh2QxbdUqYbdU'),
                         Artist('Esko', '0rQ69yrbz7CeUmXUn1beIj'),
                         Artist('Mouad Locos', '0FwFGRp5bp9KWyPiCI1CYX'),
                         Artist('JoeyAK', '4iCzh7b2cLbHVsPOwhr8W0'),
                         Artist('Young Ellens', '0SuC1Z51R9kleDO1pj3Gub'),
                         Artist('Chivv', '2hBfmHHnM4dS4pJgEJENCg'))
track_multiple = Track(artist_multiple, title_multiple, artist_tuple_multiple, spotify_id_multiple)

# Song with single artists
title_single = 'Yesterday'
spotify_id_single = '3BQHpFgAp4l80e1XslIjNI'
artist_single = 'The Beatles'
artist_tuple_single = (Artist('The Beatles', '3WrFJ7ztbogyGnTHbHJFl2'),)
track_single = Track(artist_single, title_single, artist_tuple_single, spotify_id_single)

# Song sets
songset_single = SongSet({track_single, })
songset_multiple = SongSet({track_multiple, })
songset_all = SongSet({track_multiple, track_single})

# Table results
song_table_single = [{'title': title_single, 'artists': artist_single}]
song_table_multiple = [{'title': title_multiple, 'artists': artist_multiple}]

track_table_single = [{'song_id': 1, 'spotify_track_id': spotify_id_single, 'active': 1}]
track_table_multiple = [{'song_id': 1, 'spotify_track_id': spotify_id_multiple, 'active': 1}]

artist_table_single = [{'name': artist.name, 'spotify_artist_id': artist.spotify_id} for artist in artist_tuple_single]
artist_table_multiple = [{'name': artist.name, 'spotify_artist_id': artist.spotify_id}
                         for artist in artist_tuple_multiple]

song_artist_table_single = [{'song_id': 1, 'artist_id': 1}]
song_artist_table_multiple = [{'song_id': 1, 'artist_id': i + 1} for i, artist in enumerate(artist_tuple_multiple)]

song_state_table = [{'song_id': 1, 'learning_state_id': 0, 'song_in_playlist': 0,
                     'next_date': util.date_from_today(0)}]

song_state_hist_table = \
    [song_state_table[0] | {'row_start': util.current_timestamp(), 'row_end': '2100-01-01 00:00:00', 'row_active': 1}]

tag_table = [{'song_id': 1, 'tag': 'test'}]


track_dict_single = {'album': {'album_type': 'album', 'artists': [
    {'external_urls': {'spotify': 'https://open.spotify.com/artist/3WrFJ7ztbogyGnTHbHJFl2'},
     'href': 'https://api.spotify.com/v1/artists/3WrFJ7ztbogyGnTHbHJFl2', 'id': '3WrFJ7ztbogyGnTHbHJFl2',
     'name': 'The Beatles', 'type': 'artist', 'uri': 'spotify:artist:3WrFJ7ztbogyGnTHbHJFl2'}],
                               'available_markets': ['AD', 'AE', 'AG', 'AL', 'AM', 'AO', 'AR', 'AT', 'AU', 'AZ', 'BA',
                                                     'BB',
                                                     'BD', 'BE',
                                                     'BF', 'BG', 'BH', 'BI', 'BJ', 'BN', 'BO', 'BR', 'BS', 'BT', 'BW',
                                                     'BY',
                                                     'BZ', 'CA',
                                                     'CD', 'CG', 'CH', 'CI', 'CL', 'CM', 'CO', 'CR', 'CV', 'CW', 'CY',
                                                     'CZ',
                                                     'DE', 'DJ',
                                                     'DK', 'DM', 'DO', 'DZ', 'EC', 'EE', 'EG', 'ES', 'FI', 'FJ', 'FM',
                                                     'FR',
                                                     'GA', 'GB',
                                                     'GD', 'GE', 'GH', 'GM', 'GN', 'GQ', 'GR', 'GT', 'GW', 'GY', 'HK',
                                                     'HN',
                                                     'HR', 'HT',
                                                     'HU', 'ID', 'IE', 'IL', 'IN', 'IQ', 'IS', 'IT', 'JM', 'JO', 'JP',
                                                     'KE',
                                                     'KG', 'KH',
                                                     'KI', 'KM', 'KN', 'KR', 'KW', 'KZ', 'LA', 'LB', 'LC', 'LI', 'LK',
                                                     'LR',
                                                     'LS', 'LT',
                                                     'LU', 'LV', 'LY', 'MA', 'MC', 'MD', 'ME', 'MG', 'MH', 'MK', 'ML',
                                                     'MN',
                                                     'MO', 'MR',
                                                     'MT', 'MU', 'MV', 'MW', 'MX', 'MY', 'MZ', 'NA', 'NE', 'NG', 'NI',
                                                     'NL',
                                                     'NO', 'NP',
                                                     'NR', 'NZ', 'OM', 'PA', 'PE', 'PG', 'PH', 'PK', 'PL', 'PS', 'PT',
                                                     'PW',
                                                     'PY', 'QA',
                                                     'RO', 'RS', 'RW', 'SA', 'SB', 'SC', 'SE', 'SG', 'SI', 'SK', 'SL',
                                                     'SM',
                                                     'SN', 'SR',
                                                     'ST', 'SV', 'SZ', 'TD', 'TG', 'TH', 'TJ', 'TL', 'TN', 'TO', 'TR',
                                                     'TT',
                                                     'TV', 'TW',
                                                     'TZ', 'UA', 'UG', 'US', 'UY', 'UZ', 'VC', 'VE', 'VN', 'VU', 'WS',
                                                     'XK',
                                                     'ZA', 'ZM',
                                                     'ZW'],
                               'external_urls': {'spotify': 'https://open.spotify.com/album/0PT5m6hwPRrpBwIHVnvbFX'},
                               'href': 'https://api.spotify.com/v1/albums/0PT5m6hwPRrpBwIHVnvbFX',
                               'id': '0PT5m6hwPRrpBwIHVnvbFX',
                               'images': [
                                   {'height': 64,
                                    'url': 'https://i.scdn.co/image/ab67616d00004851e3e3b64cea45265469d4cafa',
                                    'width': 64},
                                   {'height': 300,
                                    'url': 'https://i.scdn.co/image/ab67616d00001e02e3e3b64cea45265469d4cafa',
                                    'width': 300},
                                   {'height': 640,
                                    'url': 'https://i.scdn.co/image/ab67616d0000b273e3e3b64cea45265469d4cafa',
                                    'width': 640}], 'name': 'Help! (Remastered)', 'release_date': '1965-08-06',
                               'release_date_precision': 'day', 'total_tracks': 14, 'type': 'album',
                               'uri': 'spotify:album:0PT5m6hwPRrpBwIHVnvbFX'}, 'artists': [
    {'external_urls': {'spotify': 'https://open.spotify.com/artist/3WrFJ7ztbogyGnTHbHJFl2'},
     'href': 'https://api.spotify.com/v1/artists/3WrFJ7ztbogyGnTHbHJFl2', 'id': '3WrFJ7ztbogyGnTHbHJFl2',
     'name': 'The Beatles', 'type': 'artist', 'uri': 'spotify:artist:3WrFJ7ztbogyGnTHbHJFl2'}],
                     'available_markets': ['AD', 'AE', 'AG', 'AL', 'AM', 'AO', 'AR', 'AT', 'AU', 'AZ', 'BA', 'BB', 'BD',
                                           'BE',
                                           'BF',
                                           'BG', 'BH', 'BI', 'BJ', 'BN', 'BO', 'BR', 'BS', 'BT', 'BW', 'BY', 'BZ', 'CA',
                                           'CD',
                                           'CG',
                                           'CH', 'CI', 'CL', 'CM', 'CO', 'CR', 'CV', 'CW', 'CY', 'CZ', 'DE', 'DJ', 'DK',
                                           'DM',
                                           'DO',
                                           'DZ', 'EC', 'EE', 'EG', 'ES', 'FI', 'FJ', 'FM', 'FR', 'GA', 'GB', 'GD', 'GE',
                                           'GH',
                                           'GM',
                                           'GN', 'GQ', 'GR', 'GT', 'GW', 'GY', 'HK', 'HN', 'HR', 'HT', 'HU', 'ID', 'IE',
                                           'IL',
                                           'IN',
                                           'IQ', 'IS', 'IT', 'JM', 'JO', 'JP', 'KE', 'KG', 'KH', 'KI', 'KM', 'KN', 'KR',
                                           'KW',
                                           'KZ',
                                           'LA', 'LB', 'LC', 'LI', 'LK', 'LR', 'LS', 'LT', 'LU', 'LV', 'LY', 'MA', 'MC',
                                           'MD',
                                           'ME',
                                           'MG', 'MH', 'MK', 'ML', 'MN', 'MO', 'MR', 'MT', 'MU', 'MV', 'MW', 'MX', 'MY',
                                           'MZ',
                                           'NA',
                                           'NE', 'NG', 'NI', 'NL', 'NO', 'NP', 'NR', 'NZ', 'OM', 'PA', 'PE', 'PG', 'PH',
                                           'PK',
                                           'PL',
                                           'PS', 'PT', 'PW', 'PY', 'QA', 'RO', 'RS', 'RW', 'SA', 'SB', 'SC', 'SE', 'SG',
                                           'SI',
                                           'SK',
                                           'SL', 'SM', 'SN', 'SR', 'ST', 'SV', 'SZ', 'TD', 'TG', 'TH', 'TJ', 'TL', 'TN',
                                           'TO',
                                           'TR',
                                           'TT', 'TV', 'TW', 'TZ', 'UA', 'UG', 'US', 'UY', 'UZ', 'VC', 'VE', 'VN', 'VU',
                                           'WS',
                                           'XK',
                                           'ZA', 'ZM', 'ZW'], 'disc_number': 1, 'duration_ms': 125666,
                     'explicit': False,
                     'external_ids': {'isrc': 'GBAYE0601477'},
                     'external_urls': {'spotify': 'https://open.spotify.com/track/3BQHpFgAp4l80e1XslIjNI'},
                     'href': 'https://api.spotify.com/v1/tracks/3BQHpFgAp4l80e1XslIjNI', 'id': '3BQHpFgAp4l80e1XslIjNI',
                     'is_local': False, 'name': 'Yesterday - Remastered 2009', 'popularity': 76,
                     'preview_url': 'https://p.scdn.co/mp3-preview/a0fdcc915706c0dcbd4e2c072bff70b9996d1733?cid'
                                    '=384795e4026e4a4f9714fe80c0a229f0',
                     'track_number': 13, 'type': 'track', 'uri': 'spotify:track:3BQHpFgAp4l80e1XslIjNI'}

track_dict_multiple = {'album': {'album_type': 'single', 'artists': [
    {'external_urls': {'spotify': 'https://open.spotify.com/artist/1zmmIiBBODh2QxbdUqYbdU'},
     'href': 'https://api.spotify.com/v1/artists/1zmmIiBBODh2QxbdUqYbdU', 'id': '1zmmIiBBODh2QxbdUqYbdU',
     'name': 'The Blockparty', 'type': 'artist', 'uri': 'spotify:artist:1zmmIiBBODh2QxbdUqYbdU'},
    {'external_urls': {'spotify': 'https://open.spotify.com/artist/0rQ69yrbz7CeUmXUn1beIj'},
     'href': 'https://api.spotify.com/v1/artists/0rQ69yrbz7CeUmXUn1beIj', 'id': '0rQ69yrbz7CeUmXUn1beIj',
     'name': 'Esko', 'type': 'artist', 'uri': 'spotify:artist:0rQ69yrbz7CeUmXUn1beIj'}],
                                 'available_markets': ['AD', 'AE', 'AG', 'AL', 'AM', 'AO', 'AR', 'AT', 'AU', 'AZ', 'BA',
                                                       'BB', 'BD', 'BE',
                                                       'BF', 'BG', 'BH', 'BI', 'BJ', 'BN', 'BO', 'BR', 'BS', 'BT', 'BW',
                                                       'BY', 'BZ', 'CA',
                                                       'CD', 'CG', 'CH', 'CI', 'CL', 'CM', 'CO', 'CR', 'CV', 'CW', 'CY',
                                                       'CZ', 'DE', 'DJ',
                                                       'DK', 'DM', 'DO', 'DZ', 'EC', 'EE', 'EG', 'ES', 'FI', 'FJ', 'FM',
                                                       'FR', 'GA', 'GB',
                                                       'GD', 'GE', 'GH', 'GM', 'GN', 'GQ', 'GR', 'GT', 'GW', 'GY', 'HK',
                                                       'HN', 'HR', 'HT',
                                                       'HU', 'ID', 'IE', 'IL', 'IN', 'IQ', 'IS', 'IT', 'JM', 'JO', 'JP',
                                                       'KE', 'KG', 'KH',
                                                       'KI', 'KM', 'KN', 'KR', 'KW', 'KZ', 'LA', 'LB', 'LC', 'LI', 'LK',
                                                       'LR', 'LS', 'LT',
                                                       'LU', 'LV', 'LY', 'MA', 'MC', 'MD', 'ME', 'MG', 'MH', 'MK', 'ML',
                                                       'MN', 'MO', 'MR',
                                                       'MT', 'MU', 'MV', 'MW', 'MX', 'MY', 'MZ', 'NA', 'NE', 'NG', 'NI',
                                                       'NL', 'NO', 'NP',
                                                       'NR', 'NZ', 'OM', 'PA', 'PE', 'PG', 'PH', 'PK', 'PL', 'PS', 'PT',
                                                       'PW', 'PY', 'QA',
                                                       'RO', 'RS', 'RW', 'SA', 'SB', 'SC', 'SE', 'SG', 'SI', 'SK', 'SL',
                                                       'SM', 'SN', 'SR',
                                                       'ST', 'SV', 'SZ', 'TD', 'TG', 'TH', 'TJ', 'TL', 'TN', 'TO', 'TR',
                                                       'TT', 'TV', 'TW',
                                                       'TZ', 'UA', 'UG', 'US', 'UY', 'UZ', 'VC', 'VE', 'VN', 'VU', 'WS',
                                                       'XK', 'ZA', 'ZM',
                                                       'ZW'],
                                 'external_urls': {'spotify': 'https://open.spotify.com/album/328i3kkPuVgmXR7H0HbVNU'},
                                 'href': 'https://api.spotify.com/v1/albums/328i3kkPuVgmXR7H0HbVNU',
                                 'id': '328i3kkPuVgmXR7H0HbVNU',
                                 'images': [{'height': 64,
                                             'url': 'https://i.scdn.co/image/ab67616d00004851ca492e80bcbe2960ca23bcfb',
                                             'width': 64},
                                            {'height': 300,
                                             'url': 'https://i.scdn.co/image/ab67616d00001e02ca492e80bcbe2960ca23bcfb',
                                             'width': 300},
                                            {'height': 640,
                                             'url': 'https://i.scdn.co/image/ab67616d0000b273ca492e80bcbe2960ca23bcfb',
                                             'width': 640}], 'name': 'HUTS', 'release_date': '2018-11-09',
                                 'release_date_precision': 'day', 'total_tracks': 2, 'type': 'album',
                                 'uri': 'spotify:album:328i3kkPuVgmXR7H0HbVNU'}, 'artists': [
    {'external_urls': {'spotify': 'https://open.spotify.com/artist/1zmmIiBBODh2QxbdUqYbdU'},
     'href': 'https://api.spotify.com/v1/artists/1zmmIiBBODh2QxbdUqYbdU', 'id': '1zmmIiBBODh2QxbdUqYbdU',
     'name': 'The Blockparty', 'type': 'artist', 'uri': 'spotify:artist:1zmmIiBBODh2QxbdUqYbdU'},
    {'external_urls': {'spotify': 'https://open.spotify.com/artist/0rQ69yrbz7CeUmXUn1beIj'},
     'href': 'https://api.spotify.com/v1/artists/0rQ69yrbz7CeUmXUn1beIj', 'id': '0rQ69yrbz7CeUmXUn1beIj',
     'name': 'Esko', 'type': 'artist', 'uri': 'spotify:artist:0rQ69yrbz7CeUmXUn1beIj'},
    {'external_urls': {'spotify': 'https://open.spotify.com/artist/0FwFGRp5bp9KWyPiCI1CYX'},
     'href': 'https://api.spotify.com/v1/artists/0FwFGRp5bp9KWyPiCI1CYX', 'id': '0FwFGRp5bp9KWyPiCI1CYX',
     'name': 'Mouad Locos', 'type': 'artist', 'uri': 'spotify:artist:0FwFGRp5bp9KWyPiCI1CYX'},
    {'external_urls': {'spotify': 'https://open.spotify.com/artist/4iCzh7b2cLbHVsPOwhr8W0'},
     'href': 'https://api.spotify.com/v1/artists/4iCzh7b2cLbHVsPOwhr8W0', 'id': '4iCzh7b2cLbHVsPOwhr8W0',
     'name': 'JoeyAK', 'type': 'artist', 'uri': 'spotify:artist:4iCzh7b2cLbHVsPOwhr8W0'},
    {'external_urls': {'spotify': 'https://open.spotify.com/artist/0SuC1Z51R9kleDO1pj3Gub'},
     'href': 'https://api.spotify.com/v1/artists/0SuC1Z51R9kleDO1pj3Gub', 'id': '0SuC1Z51R9kleDO1pj3Gub',
     'name': 'Young Ellens', 'type': 'artist', 'uri': 'spotify:artist:0SuC1Z51R9kleDO1pj3Gub'},
    {'external_urls': {'spotify': 'https://open.spotify.com/artist/2hBfmHHnM4dS4pJgEJENCg'},
     'href': 'https://api.spotify.com/v1/artists/2hBfmHHnM4dS4pJgEJENCg', 'id': '2hBfmHHnM4dS4pJgEJENCg',
     'name': 'Chivv', 'type': 'artist', 'uri': 'spotify:artist:2hBfmHHnM4dS4pJgEJENCg'}],
                       'available_markets': ['AD', 'AE', 'AG', 'AL', 'AM', 'AO', 'AR', 'AT', 'AU', 'AZ', 'BA', 'BB',
                                             'BD', 'BE', 'BF',
                                             'BG', 'BH', 'BI', 'BJ', 'BN', 'BO', 'BR', 'BS', 'BT', 'BW', 'BY', 'BZ',
                                             'CA', 'CD', 'CG',
                                             'CH', 'CI', 'CL', 'CM', 'CO', 'CR', 'CV', 'CW', 'CY', 'CZ', 'DE', 'DJ',
                                             'DK', 'DM', 'DO',
                                             'DZ', 'EC', 'EE', 'EG', 'ES', 'FI', 'FJ', 'FM', 'FR', 'GA', 'GB', 'GD',
                                             'GE', 'GH', 'GM',
                                             'GN', 'GQ', 'GR', 'GT', 'GW', 'GY', 'HK', 'HN', 'HR', 'HT', 'HU', 'ID',
                                             'IE', 'IL', 'IN',
                                             'IQ', 'IS', 'IT', 'JM', 'JO', 'JP', 'KE', 'KG', 'KH', 'KI', 'KM', 'KN',
                                             'KR', 'KW', 'KZ',
                                             'LA', 'LB', 'LC', 'LI', 'LK', 'LR', 'LS', 'LT', 'LU', 'LV', 'LY', 'MA',
                                             'MC', 'MD', 'ME',
                                             'MG', 'MH', 'MK', 'ML', 'MN', 'MO', 'MR', 'MT', 'MU', 'MV', 'MW', 'MX',
                                             'MY', 'MZ', 'NA',
                                             'NE', 'NG', 'NI', 'NL', 'NO', 'NP', 'NR', 'NZ', 'OM', 'PA', 'PE', 'PG',
                                             'PH', 'PK', 'PL',
                                             'PS', 'PT', 'PW', 'PY', 'QA', 'RO', 'RS', 'RW', 'SA', 'SB', 'SC', 'SE',
                                             'SG', 'SI', 'SK',
                                             'SL', 'SM', 'SN', 'SR', 'ST', 'SV', 'SZ', 'TD', 'TG', 'TH', 'TJ', 'TL',
                                             'TN', 'TO', 'TR',
                                             'TT', 'TV', 'TW', 'TZ', 'UA', 'UG', 'US', 'UY', 'UZ', 'VC', 'VE', 'VN',
                                             'VU', 'WS', 'XK',
                                             'ZA', 'ZM', 'ZW'], 'disc_number': 1, 'duration_ms': 228336,
                       'explicit': True,
                       'external_ids': {'isrc': 'NLS241800525'},
                       'external_urls': {'spotify': 'https://open.spotify.com/track/0UMaqPntFC8dFOc7p3Iefj'},
                       'href': 'https://api.spotify.com/v1/tracks/0UMaqPntFC8dFOc7p3Iefj',
                       'id': '0UMaqPntFC8dFOc7p3Iefj',
                       'is_local': False, 'name': 'HUTS', 'popularity': 50,
                       'preview_url': 'https://p.scdn.co/mp3-preview/c8c1764446e8be31186458daef217ae0fd6df5db?cid'
                                      '=384795e4026e4a4f9714fe80c0a229f0',
                       'track_number': 1, 'type': 'track', 'uri': 'spotify:track:0UMaqPntFC8dFOc7p3Iefj'}

playlist_dict = {'href': 'https://api.spotify.com/v1/users/11128259870/playlists?offset=0&limit=50', 'items': [
    {'collaborative': False, 'description': '',
     'external_urls': {'spotify': 'https://open.spotify.com/playlist/10HENRMHjgHTaMuT7GaBee'},
     'href': 'https://api.spotify.com/v1/playlists/10HENRMHjgHTaMuT7GaBee', 'id': '10HENRMHjgHTaMuT7GaBee',
     'images': [{'height': 640,
                 'url': 'https://mosaic.scdn.co/640/ab67616d0000b27366c5790096354289a8d063a7ab67616d0000b27384eed528034567f3ec4da34cab67616d0000b273aa1beea495a0070294c30e31ab67616d0000b273bd26ede1ae69327010d49946',
                 'width': 640}, {'height': 300,
                                 'url': 'https://mosaic.scdn.co/300/ab67616d0000b27366c5790096354289a8d063a7ab67616d0000b27384eed528034567f3ec4da34cab67616d0000b273aa1beea495a0070294c30e31ab67616d0000b273bd26ede1ae69327010d49946',
                                 'width': 300}, {'height': 60,
                                                 'url': 'https://mosaic.scdn.co/60/ab67616d0000b27366c5790096354289a8d063a7ab67616d0000b27384eed528034567f3ec4da34cab67616d0000b273aa1beea495a0070294c30e31ab67616d0000b273bd26ede1ae69327010d49946',
                                                 'width': 60}], 'name': 'Lijst voor dj',
     'owner': {'display_name': 'Bart Portegijs',
               'external_urls': {'spotify': 'https://open.spotify.com/user/11128259870'},
               'href': 'https://api.spotify.com/v1/users/11128259870', 'id': '11128259870', 'type': 'user',
               'uri': 'spotify:user:11128259870'}, 'primary_color': None, 'public': False,
     'snapshot_id': 'NDQsZDAxOWRhMzRmMGZhYzczMzVkMzhmYzRlMjQ0Y2RiYjZlZDczNDM3Mw==',
     'tracks': {'href': 'https://api.spotify.com/v1/playlists/10HENRMHjgHTaMuT7GaBee/tracks', 'total': 26},
     'type': 'playlist', 'uri': 'spotify:playlist:10HENRMHjgHTaMuT7GaBee'}
],
                 'limit': 50, 'next': 'https://api.spotify.com/v1/users/11128259870/playlists?offset=50&limit=50',
                 'offset': 0,
                 'previous': None, 'total': 53}

playlist_name = 'Lijst voor dj'
playlist_spotify_id = '10HENRMHjgHTaMuT7GaBee'
