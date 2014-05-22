import unittest

from ott.data.content.adverts import Adverts 
from ott.data.content.fares import Fares

class TestStuff(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_adverts(self):
        a = Adverts("http://trimet.org/map/adverts/")
        q = a.query()
        print q
        self.assertEqual(q['project'], 'test')


    def test_fares(self):
        f = Fares("http://trimet.org/map/fares/fares.json")
        q = f.query()
        print q
        self.assertEqual(f['project'], 'test')


