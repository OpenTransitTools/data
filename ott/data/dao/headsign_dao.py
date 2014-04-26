import logging
log = logging.getLogger(__file__)

from .base_dao import BaseDao
from .alerts_dao import AlertsDao

class HeadsignDao(BaseDao):
    ''' List of HeadsignDao data objects
            "1" : {
                "route_id" : "1",
                "dir"   : "1",
                "name"  : "1 Vermont to 45th Ave",
                "route_url"    : "http://trimet.org/schedules/r001.htm",
                "arrival_url"  : "http://trimet.org/arrivals/tracker.html?locationID=7765&route=1",
                "ntimes" : 6,
                "ptimes" : 0.6,
                "has_alert" : True # see make_alerts() routine below...
            }
    '''
    def __init__(self, hs):
        super(HeadsignDao, self).__init__()
        self.route_id = hs.route.route_id
        self.stop_id = hs.stop_id
        self.headsign = hs.headsign
        self.route_name = hs.route.name
        self.sort_order = hs.route.sort_order

    @classmethod
    def from_route(cls, route):
        ''' make a HeadsignDao from a gtfs route object
        '''
        from gtfsdb import Route

