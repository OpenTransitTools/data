import unittest

from ott.data.content.adverts import Adverts 
from ott.data.content.fares import Fares
from ott.data.content.cancelled_routes import CancelledRoutes


class TestStuff(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_fares(self):
        self.assertNotEqual('2', '$2.50')
