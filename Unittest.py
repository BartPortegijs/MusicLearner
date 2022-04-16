import unittest
from data import Playlist, connect_spotify_from_config, Track

class TestPlaylistCreation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        global sp 
        sp = connect_spotify_from_config("configfile.ini")

    @classmethod
    def tearDownClass(cls):
        "Delete spotify connection"
        global sp
        del(sp)

    def tearDown(cls):
        "Remove unittest playlist."
        pl = Playlist.find(sp, 'Unittest playlist', verbose=False)
        if pl is not None: pl.delete() 

    def test_find_non_existing_playlist(self):
        "Checks that finding non-existent playlist results in none."
        self.playlist_instance_found = Playlist.find(sp, 'Unittest playlist', verbose= False)
        self.assertIsNone(self.playlist_instance_found)

    def test_find_existing_playlist(self):
        "Checks that finding existing playlist results in a variable"
        self.playlist_instance_created = Playlist.create(sp, 'Unittest playlist')
        self.playlist_instance_found = Playlist.find(sp, 'Unittest playlist')
        self.assertIsNotNone(self.playlist_instance_found)

    def test_create_playlist(self):
        "Checks that creating playlist works."
        self.playlist_instance_created = Playlist.create(sp, 'Unittest playlist')
        self.playlist_instance_found = Playlist.find(sp, 'Unittest playlist')
        self.assertEqual(vars(self.playlist_instance_created), 
                        vars(self.playlist_instance_found))

    def test_remove_playlist(self):
        "Check that playlist can be removed"
        self.playlist_instance_created = Playlist.create(sp, 'Unittest playlist')
        self.playlist_instance_created.delete()
        self.test_find_non_existing_playlist()

class TestTrackComparison(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        global sp 
        sp = connect_spotify_from_config("configfile.ini")

    @classmethod
    def tearDownClass(cls):
        "Delete spotify connection"
        global sp
        del(sp)

    def test_equality(self):
        "Checks that comparison betwee same tracks return equality."
        self.assertEqual(Track.from_id(sp, '0IkK4SEryuCtbQjm5LRLMZ'), Track.from_id(sp, '0IkK4SEryuCtbQjm5LRLMZ'))

    def test_equality_same_repres(self):
        self.assertEqual(Track.from_id(sp, '0IkK4SEryuCtbQjm5LRLMZ'), Track.from_id(sp, '3rmo8F54jFF8OgYsqTxm5d'))    

    def test_inequality(self):
        self.assertNotEqual(Track.from_id(sp, '0IkK4SEryuCtbQjm5LRLMZ'), Track.from_id(sp, '12N23tQKmfGcEO0z8ObwtM'))




if __name__ == '__main__':
    unittest.main()