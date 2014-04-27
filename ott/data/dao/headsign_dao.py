import logging
log = logging.getLogger(__file__)

from .base_dao import BaseDao
from .alerts_dao import AlertsDao

from ott.utils import object_utils

class StopHeadsignDao(BaseDao):
    ''' List of StopHeadsignDao data objects
            "0AI3Mk6FErSH4Q==" : {
                "stop_id"   : "2",
                "route_id"  : "1",
                "route_name": "1 Vermont",
                "headsign"  : "45th Ave",
                "dir"       : "1",
                "sort_order": 1,
                "has_alert" : True
            }
    '''
    def __init__(self, stop_time, has_alert=False):
        super(StopHeadsignDao, self).__init__()
        self.stop_id = stop_time.stop_id
        self.route_id = stop_time.trip.route.route_id
        self.route_name = stop_time.trip.route.route_name
        self.headsign = self.get_headsign(stop_time)
        self.sort_order = stop_time.trip.route.route_sort_order
        self.has_alert = has_alert

    @classmethod
    def get_headsign(cls, stop_time):
        return stop_time.stop_headsign or stop_time.trip.trip_headsign

    @classmethod
    def unique_id(cls, stop_time):
        hs = "{0}-{1}-{2}".format(stop_time.trip.route_id, stop_time.stop_id, cls.get_headsign(stop_time))
        uid = object_utils.to_hash(hs)
        return uid 

