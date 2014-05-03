import logging
log = logging.getLogger(__file__)

from .base_dao   import BaseDao
from .route_dao  import RouteDao
from .alerts_dao import AlertsDao

from gtfsdb import Stop
Stop.make_geom_lazy()

from ott.utils   import num_utils


class StopListDao(BaseDao):
    ''' List of StopDao data objects ... both list and contents ready for marshaling into JSON
    '''
    def __init__(self, stops, name=None):
        super(StopListDao, self).__init__()
        self.stops = stops
        self.count = len(stops)
        self.name  = name

    @classmethod
    def from_routestops_orm(cls, route_stops, agency="TODO", detailed=False):
        ''' make a StopListDao based on a route_stops object
        '''
        ret_val = None
        if route_stops and len(route_stops) > 0:
            stops = []
            for rs in route_stops:
                stop = StopDao.from_stop_orm(stop=rs.stop, order=rs.order, agency=agency, detailed=detailed)
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
        stops_orm = session.query(Stop).order_by(Stop.geom.distance(point)).limit(geo_params.limit)

        # step 3a: loop thru nearest N stops
        stops = []
        for s in stops_orm:
            # step 3b: calculate distance 
            dist = num_utils.distance_mi(s.stop_lat, s.stop_lon, geo_params.lat, geo_params.lon)

            # step 3c: make stop...
            stop = StopDao.from_stop_orm(stop=s, distance=dist, agency=geo_params.agency, detailed=geo_params.detailed)
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

        # process the list of routes serving the stop
        


        '''
        if templates:
            self.arrival_url, self.has_arrival_url = templates.get_arrival_url(self)
            self.from_planner_url, self.has_from_planner_url = templates.get_from_planner_url(self)
            self.to_planner_url, self.has_to_planner_url = templates.get_to_planner_url(self)
            self.stop_img_url, self.has_stop_img_url = templates.get_stop_img_url(self)
            self.map_url, self.has_map_url = templates.get_map_url(self)
        '''

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

    @classmethod
    def from_stop_orm(cls, stop, distance=0.0, order=0, agency="TODO", detailed=True):
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

            #from sqlalchemy.orm import object_session
            #alerts = AlertsDao.get_stop_alerts(object_session(stop), stop.stop_id)

        # step 2: query db for route ids serving this stop...
        ret_val = StopDao(stop, amenities, routes, alerts, distance, order)
        return ret_val


    @classmethod
    def from_stop_id(cls, session, stop_id, distance=0.0, agency="TODO", detailed=True):
        ''' make a StopDao from a stop_id and session ... and maybe templates
        '''
        #import pdb; pdb.set_trace()
        stop = session.query(Stop).filter(Stop.stop_id == stop_id).one()
        ret_val = cls.from_stop_orm(stop, distance, agency=agency, detailed=detailed)
        return ret_val

