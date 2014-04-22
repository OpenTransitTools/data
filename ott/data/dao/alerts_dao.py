import datetime
import logging
log = logging.getLogger(__file__)

from .base_dao import BaseDao
from ..gtfsrdb import query
from ott.utils import object_utils
from ott.utils import date_utils
from ott.utils import transit_utils

class AlertsDao(BaseDao):
    def __init__(self):
        super(AlertsDao, self).__init__()
        self.route_id = None
        self.alert_id = None
        self.stop_id  = None
        self.trip_id  = None
        self.url      = None
        self.header_text      = None
        self.description_text = None
        self.cause  = None
        self.effect = None
        self.start  = None
        self.end    = None
        self.is_current        = False
        self.pretty_start_date = None
        self.pretty_start_time = None
        self.pretty_end_date   = None
        self.pretty_end_time   = None
        self.route_short_names = []

    def set_dates(self, start, end):
        self.start = date_utils.make_date_from_timestamp(start)
        self.pretty_start_date = date_utils.pretty_date(self.start)
        self.pretty_start_time = date_utils.pretty_time(self.start)

        end = date_utils.make_date_from_timestamp(end)
        if type(end) is datetime and end > start:
            self.end = end
            self.pretty_end_date = date_utils.pretty_date(self.end)
            self.pretty_end_time = date_utils.pretty_time(self.end)

        self.is_current = date_utils.is_date_between(self.start, self.end)

    def set_short_names(self, session, alert):
        ''' note: uses relationship to gtfsdb's Route table defined in model.py
        '''
        for n in alert.InformedEntities:
            try:
                short_name = transit_utils.make_short_name(n.route)
                if short_name:
                    self.route_short_names.append(short_name)
            except:
                pass

    def init_via_alert(self, session, alert):
        ''' init this object via this 
        '''
        object_utils.update_object(self, src=alert)
        object_utils.update_object(self, src=alert.Alert)
        self.set_dates(alert.Alert.start, alert.Alert.end)
        self.set_short_names(session, alert.Alert)


    @classmethod
    def get_route_alerts(cls, session, route_id, agency_id='NotUsed-AssumesSingleAgencyAlaTriMet'):
        ''' query GTFSrDB, and return a list of AlertResponse objects for the route
        '''
        ret_val = []
        #import pdb; pdb.set_trace()
        alerts = query.via_route_id(session, route_id, agency_id)
        for a in alerts:
            r = AlertsDao()
            r.init_via_alert(session, a)
            ret_val.append(r)
        return ret_val


    @classmethod
    def get_stop_alerts(cls, session, stop_id, agency_id='NotUsed-AssumesSingleAgencyAlaTriMet'):
        ''' query GTFSrDB, and return a list of AlertResponse objects for this stop id
        '''
        ret_val = []
        alerts = query.via_stop_id(session, stop_id, agency_id)
        for a in alerts:
            r = AlertsDao()
            r.init_via_alert(session, a)
            ret_val.append(r)
        return ret_val
