import logging
log = logging.getLogger(__file__)

from .base_dao import BaseDao
from .alerts_dao import AlertsDao

from ott.utils import object_utils

class StopHeadsignDao(BaseDao):
    ''' List of StopHeadsignDao data objects
            "1" : {
                "route_id"  : "1",
                "stop_id"   : "2",
                "route_name": "1 Vermont",
                "headsign"  : "45th Ave",
                "dir"       : "1",
                "sort_order": 1,
                "ntimes"    : 6,
                "ptimes"    : 0.6,
                "has_alert" : True # see make_alerts() routine below...
            }
    '''
    def __init__(self, stop_time):
        super(StopHeadsignDao, self).__init__()
        self.route_id = stop_time.trip.route.route_id
        self.route_name = stop_time.trip.route.route_name
        self.stop_id = stop_time.stop_id
        self.headsign = self.get_headsign(stop_time)
        self.sort_order = stop_time.trip.route.route_sort_order

    @classmethod
    def get_headsign(cls, stop_time):
        return stop_time.stop_headsign or stop_time.trip.trip_headsign

    @classmethod
    def unique_id(cls, stop_time):
        hs = "{0}-{1}-{2}".format(stop_time.trip.route_id, stop_time.stop_id, cls.get_headsign(stop_time))
        uid = object_utils.to_hash(hs)
        return uid 

