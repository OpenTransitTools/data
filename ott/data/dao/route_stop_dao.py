import logging
log = logging.getLogger(__file__)

from .base_dao import BaseDao
from .route_dao import RouteDao
from .stop_dao import StopListDao

class RouteStopDao(BaseDao):
    ''' RouteStopsDao is a collection of a RouteDao, a DirectionDao and a list of StopListDao objects
        the routes_stops are defined in created table in gtfsdb (e.g., gtfsdb loading logic requires
        that gtfs data have direction ids defined in the trip table). 
    '''
    def __init__(self, route, direction, stops):
        super(RouteStopDao, self).__init__()
        self.route = route
        self.direction = direction
        self.stops = stops

    @classmethod
    def from_route_direction(cls, session, route_id, direction_id, agency="TODO"):
        ''' make a RouteStopsDao from route_id, direction_id and session
        '''
        ret_val = None

        #import pdb; pdb.set_trace()
        from gtfsdb import RouteStop
        rs = session.query(RouteStop).filter(
                           RouteStop.route_id == route_id,
                           RouteStop.direction_id == direction_id
                     ).all()

        if rs and len(rs) > 1 and rs[0].route:
            if rs[0].route.stops:
                route = RouteDao.from_route_orm(rs[0].route, agency)
                stops = StopListDao.from_routestops_orm(rs, agency)

        #ret_val = RouteStopDao(r, session)
        return ret_val
