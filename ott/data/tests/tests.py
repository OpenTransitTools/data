import unittest

from ott.data.content.adverts import Adverts 
from ott.data.content.fares import Fares
from ott.data.content.cancelled_routes import CancelledRoutes

class TestStuff(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_adverts(self):
        a = Adverts("http://trimet.org/map/adverts/")
        q = a.query()
        self.assertGreaterEqual(len(a.content), 2)
        self.assertRegexpMatches(q[0]['content'], "trimet.org")

    def test_fares(self):
        f = Fares("http://trimet.org/map/fares/fares.json")
        q = f.query()
        self.assertGreaterEqual(len(f.content), 2)
        self.assertEqual(q, '$2.50')

    def test_cancelled_routes(self):
        f = CancelledRoutes("http://dev.trimet.org/map/cancelled_routes.json")
        q = f.query()
        self.assertGreaterEqual(len(f.content), 2)

