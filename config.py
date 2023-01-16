from data_classes import *


learning_states_input = [
    {'id': 0, 'phase': 0, 'activity': 'first_check', 'next_id_positive': 99, 'next_id_negative': 2, 'days_before_active': 0},
    {'id': 99, 'phase': 0, 'activity': 'finished', 'next_id_positive': None, 'next_id_negative': None, 'days_before_active': None},
    {'id': 1, 'phase': 1, 'activity': 'check', 'next_id_positive': 4, 'next_id_negative': 2, 'days_before_active': 1},
    {'id': 2, 'phase': 1, 'activity': 'learn', 'next_id_positive': 3, 'next_id_negative': None, 'days_before_active': 0},
    {'id': 3, 'phase': 1, 'activity': 'test', 'next_id_positive': 1, 'next_id_negative': 2, 'days_before_active': 1},

    {'id': 4, 'phase': 2, 'activity': 'check', 'next_id_positive': 7, 'next_id_negative': 5, 'days_before_active': 7},
    {'id': 5, 'phase': 2, 'activity': 'learn', 'next_id_positive': 6, 'next_id_negative': None, 'days_before_active': 0},
    {'id': 6, 'phase': 2, 'activity': 'test', 'next_id_positive': 4, 'next_id_negative': 1, 'days_before_active': 1},

    {'id': 7, 'phase': 3, 'activity': 'check', 'next_id_positive': 10, 'next_id_negative': 8, 'days_before_active': 20},
    {'id': 8, 'phase': 3, 'activity': 'learn', 'next_id_positive': 9, 'next_id_negative': None, 'days_before_active': 0},
    {'id': 9, 'phase': 3, 'activity': 'test', 'next_id_positive': 7, 'next_id_negative': 4, 'days_before_active': 1},

    {'id': 10, 'phase': 4, 'activity': 'check', 'next_id_positive': 13, 'next_id_negative': 11, 'days_before_active': 60},
    {'id': 11, 'phase': 4, 'activity': 'learn', 'next_id_positive': 12, 'next_id_negative': None, 'days_before_active': 0},
    {'id': 12, 'phase': 4, 'activity': 'test', 'next_id_positive': 10, 'next_id_negative': 7, 'days_before_active': 1},

    {'id': 13, 'phase': 5, 'activity': 'check', 'next_id_positive': 99, 'next_id_negative': 14, 'days_before_active': 180},
    {'id': 14, 'phase': 5, 'activity': 'learn', 'next_id_positive': 15, 'next_id_negative': None, 'days_before_active': 0},
    {'id': 15, 'phase': 5, 'activity': 'test', 'next_id_positive': 13, 'next_id_negative': 10, 'days_before_active': 1}
    ]


learning_states = [LearningState(**input_states) for input_states in learning_states_input]


playlist_configs = [
    PlaylistConfig(playlist=Playlist(name='first_check'),
                   rules=[ConfigRule(config_type='filter', variable='activity', sign='=', value='first_check'),
                          ConfigRule(config_type='max_nr_of_tracks', value=50)
                          ]),
    PlaylistConfig(playlist=Playlist(name='first_learn'),
                   rules=[ConfigRule(config_type='filter', variable='activity', sign='=', value='learn'),
                          ConfigRule(config_type='filter', variable='phase', sign='=', value=1),
                          ConfigRule(config_type='max_nr_of_tracks', value=20)
                          ]),
    PlaylistConfig(playlist=Playlist(name='learn'),
                   rules=[ConfigRule(config_type='filter', variable='activity', sign='=', value='learn'),
                          ConfigRule(config_type='filter', variable='phase', sign='>', value=1),
                          ConfigRule(config_type='max_nr_of_tracks', value=25),
                          ConfigRule(config_type='keep_unknown', value=True)
                          ]),
    PlaylistConfig(playlist=Playlist(name='check'),
                   rules=[ConfigRule(config_type='filter', variable='activity', sign='=', value='check')
                          ]),
    PlaylistConfig(playlist=Playlist(name='test'),
                   rules=[ConfigRule(config_type='filter', variable='activity', sign='=', value='test')
                          ]),
    PlaylistConfig(playlist=Playlist(name='known_addition'),
                   rules=[ConfigRule(config_type='introduction_state', value=99)]),
    PlaylistConfig(playlist=Playlist(name='unknown_addition'),
                   rules=[ConfigRule(config_type='introduction_state', value=2)]),
    PlaylistConfig(playlist=Playlist(name='check_addition'),
                   rules=[ConfigRule(config_type='introduction_state', value=0)]),
    PlaylistConfig(playlist=Playlist(name='remove_list'),
                   rules=[ConfigRule(config_type='remove', value=True)]),
    PlaylistConfig(playlist=Playlist(name='repeat_list'),
                   rules=[ConfigRule(config_type='repeat', value=True)])
]
