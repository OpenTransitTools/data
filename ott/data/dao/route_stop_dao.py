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
    def __init__(self, route, stops, direction):
        super(RouteStopDao, self).__init__()
        self.route = route
        self.stop_list = stops
        self.direction = direction

    @classmethod
    def from_route_direction(cls, session, route_id, direction_id, agency="TODO", detailed=False):
        ''' make a RouteStopsDao from route_id, direction_id and session
        '''
        ret_val = None

        #import pdb; pdb.set_trace()
        from gtfsdb import RouteStop
        rs = session.query(RouteStop).filter(
                           RouteStop.route_id == route_id,
                           RouteStop.direction_id == direction_id
                     ).all()

        if rs and len(rs) > 1:
            route = RouteDao.from_route_orm(rs[0].route, agency, detailed)
            stops = StopListDao.from_routestops_orm(rs, agency, detailed)
            # TODO: DirectionDao()
            ret_val = RouteStopDao(route, stops, rs[0].direction_id)

        #ret_val = RouteStopDao(r, session)
        return ret_val
