import logging
log = logging.getLogger(__file__)


from .response_base import DatabaseNotFound, ServerError, ResponseBase
from .route_response import RouteResponse

class StopListResponse(ResponseBase):
    ''' List of StopResponse data objects ... both list and contents ready for marshaling into JSON
    '''
    def __init__(self, stop_list, name, lon, lat):
        super(StopListResponse, self).__init__()
        self.stops = stop_list
        self.count = len(stop_list)
        self.name  = name
        self.lon   = lon
        self.lat   = lat


class StopResponse(ResponseBase):
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
    def __init__(self, stop, amenities, routes, templates, distance, session=None):
        super(StopResponse, self).__init__()

        #import pdb; pdb.set_trace()
        self.copy_basics(self.__dict__, stop)
        self.distance = distance

        self.amenities = amenities
        self.has_amenities = amenities and len(amenities) > 0

        # process the list of routes serving the stop
        self.routes = []
        '''
        if stop.routes is not None:
            for r in stop.routes:
                rs = RouteResponse(r, stop, session)
                self.routes.append(rs)
        '''

        #self.alerts = AlertsResponse.get_stop_alerts(session, stop.stop_id)
        #self.has_alerts = self.alerts and len(self.alerts) > 0

        if templates:
            self.arrival_url, self.has_arrival_url = templates.get_arrival_url(self)
            self.from_planner_url, self.has_from_planner_url = templates.get_from_planner_url(self)
            self.to_planner_url, self.has_to_planner_url = templates.get_to_planner_url(self)
            self.stop_img_url, self.has_stop_img_url = templates.get_stop_img_url(self)
            self.map_url, self.has_map_url = templates.get_map_url(self)

    @classmethod
    def copy_basics(cls, tgt, src):
        tgt['stop_id'] = src.stop_id
        tgt['name'] = src.stop_name
        tgt['description'] = src.stop_desc
        tgt['type'] = src.location_type
        tgt['lat'] = src.stop_lat
        tgt['lon'] = src.stop_lon

    @classmethod
    def from_stop_obj(cls, stop, session, templates=None, distance=0):
        ''' make a StopResponse from a stop object and session ... and maybe templates
        '''
        ret_val = None
        try:
            # step 1: query db for stop amenity names
            amenities = []
            for f in stop.stop_features:
                amenities.append(f.stop_feature_type.feature_name)
            amenities = sorted(list(set(amenities)))  # sorted and distinct (set) list of attributes 
    
            # step 2: query db for route ids serving this stop...
            routes = None
            #route_ids = session.query(distinct(RouteStop.route_id)).filter(RouteStop.stop_id == stop.stop_id).all()
            #route_ids = object_utils.strip_tuple_list(route_ids)
            #routes = session.query(RouteOtt).filter(RouteOtt.route_id.in_(route_ids)).order_by(RouteOtt.sort_order).all()
    
            ret_val = StopResponse(stop, amenities, routes, templates, distance, session)
        except Exception, e:
            log.warn(e)

        return ret_val


    @classmethod
    def from_stop_id(cls, stop_id, session, templates=None, distance=0):
        ''' make a StopResponse from a stop_id and session ... and maybe templates
        '''
        from gtfsdb import Stop

        ret_val = None
        try:
            stop = session.query(Stop).filter(Stop.stop_id == stop_id).one()
            ret_val = cls.from_stop_obj(stop, session, templates, distance)
        except Exception, e:
            #import pdb; pdb.set_trace()
            log.warn(e)

        return ret_val

