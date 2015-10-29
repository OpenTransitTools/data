import datetime
import logging
log = logging.getLogger(__file__)

from ott.utils.dao.base import BaseDao
from ..gtfsrdb import query
from ott.utils import object_utils
from ott.utils import date_utils


class AlertsListDao(BaseDao):
    def __init__(self, alerts):
        super(AlertsListDao, self).__init__()
        self.routes = alerts
        self.count = len(alerts)

    @classmethod
    def get_route_alerts(cls, session, route_id, agency_id='NotUsed-AssumesSingleAgencyAlaTriMet'):
        alerts = AlertsDao.get_route_alerts(session, route_id, agency_id)
        return AlertsListDao(alerts)

    @classmethod
    def get_stop_alerts(cls, session, stop_id, agency_id='NotUsed-AssumesSingleAgencyAlaTriMet'):
        alerts = AlertsDao.get_stop_alerts(session, stop_id, agency_id)
        return AlertsListDao(alerts)


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
        self.is_past = False
        self.is_distant = False
        self.is_future  = False
        self.pretty_start_date = None
        self.pretty_start_time = None
        self.pretty_end_date   = None
        self.pretty_end_time   = None
        self.route_short_names = None
        self.route_ids         = None

    def set_dates(self, start_secs, end_secs):
        #import pdb; pdb.set_trace()
        self.start = date_utils.make_date_from_timestamp(start_secs)
        self.pretty_start_date = date_utils.pretty_date(self.start)
        self.pretty_start_time = date_utils.pretty_time(self.start)

        self.is_future  = date_utils.is_future(start_secs)
        self.is_past    = date_utils.is_past(end_secs)
        self.is_distant = date_utils.is_distant(self.start)

        if end_secs > 1000:
            end = date_utils.make_date_from_timestamp(end_secs)
            if type(end) is datetime and end > self.start:
                self.end = end
                self.pretty_end_date = date_utils.pretty_date(self.end)
                self.pretty_end_time = date_utils.pretty_time(self.end)

    def init_via_alert(self, session, alert):
        ''' init this object via this 
        '''
        object_utils.update_object(self, src=alert)
        object_utils.update_object(self, src=alert.Alert)
        self.set_dates(alert.Alert.start, alert.Alert.end)

    @classmethod
    def get_route_alerts_via_orm(cls, route):
        ''' query GTFSrDB, and return a list of AlertResponse objects for the route
        '''
        ret_val = []
        alerts = query.via_route_id(session, route_id, agency_id)
        for a in alerts:
            r = AlertsDao()
            r.init_via_alert(session, a)
            ret_val.append(r)
        return ret_val

    @classmethod
    def get_route_alerts(cls, session, route_id, agency_id='NotUsed-AssumesSingleAgencyAlaTriMet'):
        ''' query GTFSrDB, and return a list of AlertResponse objects for the route
        '''
        ret_val = []
        try:
            alerts = query.via_route_id(session, route_id, agency_id)

            for a in alerts:
                r = AlertsDao()
                r.init_via_alert(session, a)
                ret_val.append(r)
            if len(ret_val) > 0:
                ret_val.sort(key=lambda x: x.start, reverse=False)
        except Exception, e:
            log.warn(e)
        return ret_val

    @classmethod
    def get_stop_alerts(cls, session, stop_id, agency_id='NotUsed-AssumesSingleAgencyAlaTriMet'):
        ''' query GTFSrDB, and return a list of AlertResponse objects for this stop id
        '''
        ret_val = []
        try:
            alerts = query.via_stop_id(session, stop_id, agency_id)
            for a in alerts:
                r = AlertsDao()
                r.init_via_alert(session, a)
                ret_val.append(r)
        except Exception, e:
            log.warn(e)
        return ret_val


def main():
    from ott.utils.db_utils import db_gtfs_rt
    session, engine = db_gtfs_rt()
    a = AlertsListDao.get_route_alerts(session, '12')
    print(a.to_json(True))
