import logging
log = logging.getLogger(__file__)

from sqlalchemy.orm import joinedload, joinedload_all
from sqlalchemy.orm import object_session

from ott.utils.dao.base import BaseDao
from .route_dao  import RouteDao
from .alerts_dao import AlertsDao

from gtfsdb import Route
from gtfsdb import Stop
#  make_geom_lazy will screw up nearest_stops
#Stop.make_geom_lazy()

from ott.utils import num_utils
from ott.utils import transit_utils


class StopListDao(BaseDao):
    ''' List of StopDao data objects ... both list and contents ready for marshaling into JSON
    '''
    def __init__(self, stops, name=None):
        super(StopListDao, self).__init__()
        self.stops = stops
        self.count = len(stops)
        self.name  = name

    @classmethod
    def from_routestops_orm(cls, route_stops, agency="TODO", detailed=False, show_alerts=False):
        ''' make a StopListDao based on a route_stops object
        '''
        ret_val = None
        if route_stops and len(route_stops) > 0:
            stops = []
            for rs in route_stops:
                stop = StopDao.from_stop_orm(rs.stop, rs.order, agency, detailed, show_alerts)
                stops.append(stop)
            ret_val = StopListDao(stops)
        return ret_val

    @classmethod
    def nearest_stops(cls, session, geo_params):
        ''' make a StopListDao based on a route_stops object
            @params: lon, lat, limit=10, name=None, agency="TODO", detailed=False): 
        '''
        #import pdb; pdb.set_trace()

        # step 1: make POINT(x,y)
        point = geo_params.to_point()

        # step 2: query database via geo routines for N of stops cloesst to the POINT
        log.info("query Stop table")  
        stops_orm = session.query(Stop).order_by(Stop.geom.distance(point)).limit(geo_params.limit)

        # step 3a: loop thru nearest N stops
        stops = []
        for s in stops_orm:
            # step 3b: calculate distance 
            dist = num_utils.distance_mi(s.stop_lat, s.stop_lon, geo_params.lat, geo_params.lon)

            # step 3c: make stop...plus add stop route short name
            stop = StopDao.from_stop_orm(stop=s, distance=dist, agency=geo_params.agency, detailed=geo_params.detailed)
            stop.add_route_short_names(stop_orm=s)
            stops.append(stop)

        # step 4: sort list then return
        stops = cls.sort_list_by_distance(stops)
        ret_val = StopListDao(stops, name=geo_params.name)
        return ret_val

    @classmethod
    def sort_list_by_distance(cls, stop_list, order=True):
        ''' sort a python list [] by distance, and assign order
        '''
        # step 1: sort the list
        stop_list.sort(key=lambda x: x.distance, reverse=False)

        # step 2: assign order
        if order:
            for i, s in enumerate(stop_list):
                s.order = i+1

        return stop_list


class StopDao(BaseDao):
    ''' Stop data object that is  ready for marshaling into JSON

    "stop_id":"7765",
    "name":"SW 6th & Jefferson",
    TODO "city":"Portland",
    "description": "X bound street in Portland
    "lat":"45.514868",
    "lon":"-122.680762",

    "stop_img_url" : "",
    "planner_url"  : "",
    "tracker_url"  : "",

    "amenities": [
        "Shelter",
        "TransitTracker Sign",
        "Schedule Display",
        "Lighting at Stop",
        "CCTV",
        "Telephone",
        "Front-door Landing Paved",
        "Back-door Landing Paved",
        "Sidewalk",
        "Traffic Signal",
        "Crosswalk",
        "Curbcut"
    ]
    ,
    "routes": [
        {"route_id":1, "name":"1-Vermont", "route_url":"http://trimet.org/schedules/r001.htm", "arrival_url":"http://trimet.org/arrivals/tracker.html?locationID=7765&route=001"}
    '''
    def __init__(self, stop, amenities, routes, alerts=None, distance=0.0, order=0):
        super(StopDao, self).__init__()
        self.copy_basics(self.__dict__, stop)
        self.routes = routes
        self.distance = distance
        self.order = order
        self.set_alerts(alerts)
        self.set_amenities(amenities)

    def find_route(self, route_id):
        ''' @return: RouteDao from the list of routes
        '''
        ret_val = None
        if route_id and self.routes:
            for r in self.routes:
                if route_id == r.route_id:
                    ret_val = r
                    break
        return ret_val

    @classmethod
    def copy_basics(cls, tgt, src):
        tgt['stop_id'] = src.stop_id
        tgt['name'] = src.stop_name
        tgt['description'] = src.stop_desc
        tgt['type'] = src.location_type
        tgt['lat'] = src.stop_lat
        tgt['lon'] = src.stop_lon

    def set_amenities(self, amenities):
        self.amenities = amenities
        if amenities and len(amenities) > 0:
            self.amenities = sorted(list(set(amenities)))  # sorted and distinct (set) list of attributes 
            self.has_amenities = True
        else:
            self.has_amenities = False

    def add_route_short_names(self, stop_orm):
        ''' add an array of short names to the DAO
        '''
        if stop_orm and stop_orm.routes is not None and len(stop_orm.routes) > 0:
            self.short_names = []
            stop_orm.routes.sort(key=lambda x: x.route_sort_order, reverse=False)
            for r in stop_orm.routes:
                sn = {'route_id':r.route_id, 'route_short_name':transit_utils.make_short_name(r)}
                self.short_names.append(sn)


    @classmethod
    def from_stop_orm(cls, stop, distance=0.0, order=0, agency="TODO", detailed=False, show_alerts=False):
        ''' make a StopDao from a stop object and session

            note that certain pages only need the simple stop info ... so we can 
            avoid queries of detailed stop info (like routes hitting a stop, alerts, etc...)
        '''

        amenities = []
        routes = []
        alerts = []

        # step 1: 
        if detailed:
            amenities = []
            for f in stop.stop_features:
                amenities.append(f.stop_feature_type.feature_name)

            if stop.routes is not None:
                for r in stop.routes:
                    rs = RouteDao.from_route_orm(r)
                    routes.append(rs)

        if show_alerts:
            alerts = AlertsDao.get_stop_alerts(object_session(stop), stop.stop_id)

        # step 2: query db for route ids serving this stop...
        ret_val = StopDao(stop, amenities, routes, alerts, distance, order)
        return ret_val


    @classmethod
    def from_stop_id(cls, session, stop_id, distance=0.0, agency="TODO", detailed=False, show_alerts=False):
        ''' make a StopDao from a stop_id and session ... and maybe templates
        '''
        #import pdb; pdb.set_trace()
        log.info("query Stop table")
        q = session.query(Stop)
        q = q.filter(Stop.stop_id == stop_id)
        if detailed:
            q = q.options(joinedload("stop_features"))
            pass
        stop = q.one()
        ret_val = cls.from_stop_orm(stop, distance, agency=agency, detailed=detailed, show_alerts=show_alerts)
        return ret_val

