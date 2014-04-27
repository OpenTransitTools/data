import logging
log = logging.getLogger(__file__)

from .base_dao import BaseDao
from .alerts_dao import AlertsDao

from gtfsdb import StopTime

class StopScheduleDao(BaseDao):
    ''' StopScheduleDao data object
    '''
    def __init__(self, stop, headsign_list, times, single_route_name, templates, session=None):
        super(StopScheduleDao, self).__init__()
        self.stop_id = stop.stop_id
        self.name = stop.stop_name
        self.city = None
        self.type = stop.location_type
        self.lat = stop.stop_lat
        self.lon = stop.stop_lon
        self.single_route_name = single_route_name # either None (for all routes at this stop) or string name for basic route name
        self.headsigns = {}
        self.schedule = self.make_schedule(headsign_list, self.headsigns, times, templates)
        self.alerts = self.make_alerts(self.headsigns, session)
        if single_route_name is None:
            # sort headsigns
            pass


    @classmethod
    def get_stop_schedule(cls, session, stop_id, date_time=None):
        '''
        '''
        if date_time is None:
            date_time = datetime.datetime.now()
    
        q = session.query(StopTime)
        q = q.filter_by(stop_id='2')
        q = q.filter(StopTime.trip.has(Trip.universal_calendar.any(date=n)))
        import pdb; pdb.set_trace()
    
        hs = []
        ids = []
        for s in q:
            id = StopHeadsignDao.unique_id(s)
            if id not in ids:
                print id
                h = StopHeadsignDao(s)
                hs.append(hs)
                print h.to_json()
        

        q = session.query(StopTime).options(joinedload('trip'))
        q = q.filter_by(stop_id=self.stop_id, )
            for r in q:
                headsign = r.stop_headsign or r.trip.trip_headsign
                self._headsigns[(r.trip.route, headsign)] += 1
        return self._headsigns


    @classmethod
    def add_headsign(cls, headsign, headsign_cache):
        id = str(headsign.id)
        if id not in headsign_cache:
            headsign_cache[id] = Headsign(headsign)
        return id

    @classmethod
    def find_headsign_id(cls, headsign_list, headsign_cache, stop_headsign, trip_headsign, route_id):
        ''' return the 'id' index into the headsign_cache dict
            note, if the headsign is not in the cache, we'll add headsign to the cache.
        '''
        #import pdb; pdb.set_trace()
        ret_val = None
        for h in headsign_list:
            if h.stop_headsign == stop_headsign and h.trip_headsign == trip_headsign and h.route_id == route_id:
                ret_val = cls.add_headsign(h, headsign_cache)
                break
        return ret_val

    @classmethod
    def make_schedule(cls, headsign_list, headsign_cache, times, templates):
        '''
            will return a list of dicts ... part of the dict has the schedule stop time, and the other the index of a given headsign
            {"t":"6:45am",  "h":"3"},
        '''
        ret_val = []
        for t in times:
            # make sure this is a stop with departure times (e.g., one can board a vehicle)
            if cls.is_boarding_stop(t):
                time = object_utils.military_to_english_time(t.departure_time)
                sign = cls.find_headsign_id(headsign_list, headsign_cache, t.stop_headsign, t.trip.trip_headsign, t.trip.route_id)
                if time and sign:
                    r = {"t":time, "h":sign}
                    ret_val.append(r)
        return ret_val

    @classmethod
    def is_boarding_stop(cls, stop_time):
        ret_val = True
        try:
            #import pdb; pdb.set_trace()
            if stop_time.pickup_type == 1:
                ret_val = false
        except:
            pass
        return ret_val


    @classmethod
    def make_alerts(cls, headsign_cache, session):
        ret_val = []

        rte_visited = []
        rte_has_alerts = []
        for h in headsign_cache.values():
            rte = str(h.route_id)
            has_alert = False

            # step 1: only call the alert service once per route (e.g., many headsigns per route)
            if rte not in rte_visited:
                rte_visited.append(rte)

                # step 2: first time seeing this route id, so call the alert service
                alerts = AlertsResponse.get_route_alerts(session, rte)

                # step 3: if this route has alerts, we'll append that list to our ret_val list
                #         and also mark the 'has_alerts' array with this route for future iterations
                if alerts:
                    ret_val = ret_val + alerts
                    rte_has_alerts.append(rte)

            # step 4: mark headsigns for route X as either having alerts or not  
            if rte in rte_has_alerts:
                has_alert = True
            h.has_alert = has_alert

        return ret_val
