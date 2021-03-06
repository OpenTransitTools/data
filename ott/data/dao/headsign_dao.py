import logging
log = logging.getLogger(__file__)

from ott.utils.dao.base import BaseDao
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
                first_time  : '03:55:22',
                last_time   : '26:11:00',
                num_trips   : 14
            }
    '''
    def __init__(self, stop_time, has_alert=False):
        super(StopHeadsignDao, self).__init__()
        self.stop_id = stop_time.stop_id
        self.route_id = stop_time.trip.route.route_id
        self.route_name = stop_time.trip.route.route_name
        self.headsign = stop_time.get_headsign()
        self.sort_order = stop_time.trip.route.route_sort_order
        self.first_time = stop_time.departure_time
        self.last_time = stop_time.departure_time
        self.num_trips = 0

    @classmethod
    def unique_id(cls, stop_time):
        hs = "{0}-{1}-{2}".format(stop_time.trip.route_id, stop_time.stop_id, stop_time.get_headsign())
        uid = object_utils.to_hash(hs)
        return uid 
