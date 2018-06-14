import datetime
import logging
log = logging.getLogger(__file__)

from ott.utils.dao.base import BaseDao
from ott.gtfsdb_realtime.model.alert_entity import AlertEntity
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

    def init_via_alert(self, alert_entity):
        """ init this object via this 
        """
        object_utils.update_object(self, src=alert_entity)
        object_utils.update_object(self, src=alert_entity.alert)
        self.set_dates(alert_entity.alert.start, alert_entity.alert.end)

        # url error checking
        if "http" not in self.url or "://" not in self.url:
            log.warn("alerts: removing 'problematic' url '{}' from response".format(self.url))
            self.url = None

    @classmethod
    def make_daos_via_alert_list(cls, alert_entity_list, results=None, reverse_sort=True):
        """ factory to create an AlertDao (service object) from AlertEntity of gtfsdb_realtime object """
        # step 1: new list and/or (optionally) appended list of results
        ret_val = results
        if ret_val is None:
            ret_val = []

        # import pdb; pdb.set_trace()

        # step 2: create new dao's from our alert list
        for ae in alert_entity_list:
            dao = cls()
            dao.init_via_alert(ae)
            ret_val.append(dao)

        # step 3: sort the lot
        if len(ret_val) > 0:
            ret_val.sort(key=lambda x: x.start, reverse=reverse_sort)

        return ret_val

    @classmethod
    def get_route_alerts(cls, session, route_id, agency_id=None):
        """
        query GTFSDB-rt and return a list of AlertResponse objects for the route
        """
        ret_val = []
        try:
            alert_entity_list = AlertEntity.query_via_route_id(session, route_id, agency_id)
            ret_val = AlertsDao.make_daos_via_alert_list(alert_entity_list)
        except Exception as e:
            log.warn(e)
        return ret_val

    @classmethod
    def get_stop_alerts(cls, session, stop_id, agency_id=None):
        """
        query GTFSDB-rt and return a list of AlertResponse objects for this stop id
        """
        ret_val = []
        try:
            alert_entity_list = AlertEntity.query_via_stop_id(session, stop_id, agency_id)
            ret_val = AlertsDao.make_daos_via_alert_list(alert_entity_list)
        except Exception as e:
            log.warn(e)
        return ret_val
