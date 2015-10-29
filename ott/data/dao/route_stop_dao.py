import logging
log = logging.getLogger(__file__)

from ott.utils.dao.base import BaseDao
from .route_dao import RouteDao
from .stop_dao import StopListDao

from gtfsdb import RouteStop


class RouteStopListDao(BaseDao):
    ''' List of RouteStopDaos for both directions of a route (or one direction if loop / uno dir)
    '''
    def __init__(self, rs, r):
        super(RouteStopListDao, self).__init__()
        self.directions = rs
        self.route = r
        self.count = len(rs)

    @classmethod
    def from_route(cls, session, route_id, direction_id=None, agency="TODO", detailed=False, active_stops_only=True):
        ''' make a StopListDao based on a route_stops object
        '''
        route = None
        route_stops = []
        dirs = [0, 1]
        if direction_id:
            dirs = [direction_id]
        for d in dirs:
            rs = RouteStopDao.from_route_direction(session, route_id, d, agency, detailed, active_stops_only)
            if rs and rs.route:
                route = rs.route
                route_stops.append(rs)
        ret_val = RouteStopListDao(route_stops, route)
        return ret_val


class RouteStopDao(BaseDao):
    ''' RouteStopsDao is a collection of a RouteDao, a DirectionDao and a list of StopListDao objects
        the routes_stops are defined in created table in gtfsdb (e.g., gtfsdb loading logic requires
        that gtfs data have direction ids defined in the trip table). 
    '''
    def __init__(self, route, stops, direction_id):
        super(RouteStopDao, self).__init__()
        self.route = route
        self.direction_id = direction_id
        self.direction_name = route.direction_0 if direction_id == 0 else route.direction_1
        self.stop_list = stops

    @classmethod
    def from_route_direction(cls, session, route_id, direction_id, agency="TODO", detailed=False, active_stops_only=True):
        ''' make a RouteStopsDao from route_id, direction_id and session
        '''
        ret_val = None

        #import pdb; pdb.set_trace()
        log.info("query RouteStop table")
        q = session.query(RouteStop).filter(
                           RouteStop.route_id == route_id,
                           RouteStop.direction_id == direction_id
                     )
        q = q.order_by(RouteStop.order)
        rs = q.all()
        if rs and len(rs) > 1:
            route = RouteDao.from_route_orm(route=rs[0].route, agency=agency, detailed=detailed)
            stops = StopListDao.from_routestops_orm(route_stops=rs, agency=agency, detailed=detailed, active_stops_only=active_stops_only)
            ret_val = RouteStopDao(route, stops, rs[0].direction_id)

        return ret_val
