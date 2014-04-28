import datetime
import logging
log = logging.getLogger(__file__)

from .base_dao import BaseDao
from .alerts_dao import AlertsDao
from .stop_dao import StopDao
from .headsign_dao import StopHeadsignDao

from ott.utils import date_utils

from gtfsdb import StopTime
from gtfsdb import Trip


class StopScheduleDao(BaseDao):
    ''' StopScheduleDao data object is contains all the schedule data at a given stop
    '''
    def __init__(self, stop, stoptimes, headsigns):
        super(StopScheduleDao, self).__init__()
        self.stop = stop
        self.stoptimes = stoptimes
        self.headsigns = headsigns

    @classmethod
    def get_stop_schedule(cls, session, stop_id, date=None, route_id=None, agency="TODO", detailed=True):
        '''
        '''
        ret_val = None

        stop = None
        headsigns = {}
        stoptimes = []


        # step 1: figure out date and time
        is_now = False
        if date is None:
            date = datetime.date.today()
            is_now = True
        now = datetime.datetime.now()

        # step 2: get stop times based on date
        q = session.query(StopTime)
        q = q.filter_by(stop_id=stop_id)
        q = q.filter(StopTime.trip.has(Trip.universal_calendar.any(date=date)))

        # step 3: optional route filter
        if route_id:
            q = q.filter(StopTime.trip.has(Trip.route_id == route_id))

        q = q.order_by(StopTime.departure_time)

        # step 4: loop through our queried stop times
        for i, st in enumerate(q):
            if cls.is_boarding_stop(st):
                # 4a: capture a stop object for later...
                if stop is None:
                    stop = StopDao.from_stop_orm(stop=st.stop, agency=agency)

                # 4b: only once, capture the route's different headsigns shown at this stop
                #     (e.g., a given route can have multiple headsignss show at this stop)
                id = StopHeadsignDao.unique_id(st)
                if not headsigns.has_key(id):
                    # make a new headsign
                    h = StopHeadsignDao(st)
                    h.sort_order += i 
                    headsigns[id] = h

                # 4c: add new stoptime to headsign cache 
                time = cls.make_stop_time(st, id, now, i+1)
                stoptimes.append(time)
                headsigns[id].last_time = st.departure_time
                headsigns[id].num_trips += 1

        # step 5: build the DAO object (assuming there was a valid stop / schedule based on the query) 
        if stop:
            ret_val = StopScheduleDao(stop, stoptimes, headsigns)

        return ret_val


    @classmethod
    def make_stop_time(cls, stoptime, headsign_id, now, order):
        ''' {"t":'12:33am', "h":'headsign_id;, "n":[E|N|L ... where E=Earlier Today, N=Now/Next, L=Later]}
        '''
        time = date_utils.military_to_english_time(stoptime.departure_time)
        #stat = date_utils.now_time_code(stoptime.departure_time, now)
        #ret_val = {"t":time, "h":headsign_id, "n":stat, "o":order}
        ret_val = {"t":time, "h":headsign_id, "o":order}
        return ret_val

    @classmethod
    def is_boarding_stop(cls, stop_time):
        ret_val = True
        try:
            #import pdb; pdb.set_trace()
            if stop_time.pickup_type == 1 or stop_time.departure_time is None:
                ret_val = False
        except:
            pass
        return ret_val



###########################
##### OLD CODE
###########################

class x():

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
