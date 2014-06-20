import datetime
import logging
log = logging.getLogger(__file__)

from ott.utils.dao.base import BaseDao
from .alerts_dao import AlertsDao
from .stop_dao import StopDao
from .headsign_dao import StopHeadsignDao

from ott.utils import date_utils

from gtfsdb import StopTime
from gtfsdb import Trip


class StopScheduleDao(BaseDao):
    ''' StopScheduleDao data object is contains all the schedule data at a given stop
    '''
    def __init__(self, stop, stoptimes, headsigns, alerts=None, route_id=None):
        super(StopScheduleDao, self).__init__()
        self.stop = stop
        self.stoptimes = stoptimes
        self.headsigns = headsigns
        self.set_alerts(alerts)
        self.single_route_id   = None
        self.single_route_name = None
        r = self.find_route(route_id)
        if r and r.name:
            self.single_route_id = route_id
            self.single_route_name = r.name


    def find_route(self, route_id):
        ''' @return: RouteDao from the stop
        '''
        
        ret_val = None
        if self.stop:
            ret_val = self.stop.find_route(route_id)
        return ret_val

    @classmethod
    def get_stop_schedule(cls, session, stop_id, date=None, route_id=None, agency="TODO", detailed=False, show_alerts=False):
        '''
        '''
        ret_val = None

        stop = None
        headsigns     = {}
        stoptimes     = []
        alerts        = []

        # step 1: figure out date and time
        is_now = False
        if date is None:
            date = datetime.date.today()
            is_now = True
        now = datetime.datetime.now()

        # step 2: get the stop schedule
        stop_times = StopTime.get_departure_schedule(session, stop_id, date, route_id)
        stop = StopDao.from_stop_id(session, stop_id, agency=agency, detailed=detailed, show_alerts=show_alerts)

        # step 4: loop through our queried stop times
        for i, st in enumerate(stop_times):
            if st.is_boarding_stop():

                # 4b: only once, capture the route's different headsigns shown at this stop
                #     (e.g., a given route can have multiple headsignss show at this stop)
                id = StopHeadsignDao.unique_id(st)
                if not headsigns.has_key(id):
                    # make a new headsign
                    h = StopHeadsignDao(st)
                    h.sort_order += len(headsigns)
                    h.id = id
                    headsigns[id] = h

                    # check to see if we have an alert for this headsign
                    #import pdb; pdb.set_trace()
                    r = stop.find_route(h.route_id)
                    if r and r.alerts and len(r.alerts) > 0:
                        h.has_alerts = True
                        # add the route to an array
                        if h.route_id not in alerts:
                            alerts.append(h.route_id)

                # 4c: add new stoptime to headsign cache 
                time = cls.make_stop_time(st, id, now, i+1)
                stoptimes.append(time)
                headsigns[id].last_time = st.departure_time
                headsigns[id].num_trips += 1

        # step 5: if we don't have a stop (and thus no stop times), we have to get something for the page to say no schedule today 
        if stop is None:
            stop = StopDao.from_stop_id(session=session, stop_id=stop_id, agency=agency, detailed=detailed, show_alerts=show_alerts)

        # step 6: build the DAO object (assuming there was a valid stop / schedule based on the query) 
        ret_val = StopScheduleDao(stop, stoptimes, headsigns, alerts, route_id)

        return ret_val

    @classmethod
    def get_stop_schedule_from_params(cls, session, params):
        ''' will make a stop schedule based on values set in ott.utils.parse.StopParamParser 
        '''
        #import pdb; pdb.set_trace()
        ret_val = cls.get_stop_schedule(session, params.stop_id, params.date, params.route_id, params.agency, params.detailed, params.alerts)
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

