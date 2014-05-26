import logging
log = logging.getLogger(__file__)

from ott.utils.dao.base import BaseDao
from .alerts_dao import AlertsDao

from sqlalchemy.orm import object_session
from gtfsdb import Route
try: Route.make_geom_lazy()
except: pass

class RouteListDao(BaseDao):
    ''' List of RouteDao data objects ... both list and RouteDao content ready for marshaling into JSON
    '''
    def __init__(self, routes):
        super(RouteListDao, self).__init__()
        self.routes = routes
        self.count = len(routes)

    @classmethod
    def route_list(cls, session, agency="TODO", detailed=False, show_alerts=False):
        ''' make a list of RouteDao objects by query to the database
        '''
        ### TODO: list of BANNED ROUTES ...
        log.info("query Route table")
        route_list = []
        routes = session.query(Route).order_by(Route.route_sort_order)
        for r in routes:
            rte = RouteDao.from_route_orm(route=r, agency=agency, detailed=detailed, show_alerts=show_alerts)
            route_list.append(rte)

        ret_val = RouteListDao(route_list)
        return ret_val


class RouteDao(BaseDao):
    ''' RouteDao data object ready for marshaling into JSON
    '''
    def __init__(self, route, alerts):
        super(RouteDao, self).__init__()
        #import pdb; pdb.set_trace()
        self.copy(route)
        self.set_alerts(alerts)

    def copy(self, r):
        self.name = r.route_name
        self.route_id = r.route_id
        self.short_name = r.route_short_name
        self.sort_order = r.route_sort_order
        self.add_route_dirs(r)

    def add_route_dirs(self, route):
        ''' 
        '''
        # step 0: two direction name vars
        dir0=None
        dir1=None

        # step 1: figure out what (if any) 'primary' direction names for this route exist in directions '0' and '1'
        try:
            for d in route.directions:
                if d.direction_id == 0:
                    dir0 = d.direction_name
                elif d.direction_id == 1:
                    dir1 = d.direction_name
        except:
            pass

        # step 2: assign direction names (or default null values) to route
        self.copy_dirs(dir0, dir1)

    # TODO we shuld really havea DirectionDao (spellin' intentional) 
    def copy_dirs(self, dir0=None, dir1=None):
        self.direction_0 = dir0
        self.direction_1 = dir1


    @classmethod
    def from_route_orm(cls, route, agency="TODO", detailed=False, show_alerts=False):
        alerts = []

        if show_alerts:
            alerts = AlertsDao.get_route_alerts(object_session(route), route.route_id)

        ret_val = RouteDao(route, alerts)
        return ret_val

    @classmethod
    def from_route_id(cls, session, route_id, agency="TODO", detailed=False, show_alerts=False):
        ''' make a RouteDao from a route_id and session
        '''
        #import pdb; pdb.set_trace()
        log.info("query Route table")
        route = session.query(Route).filter(Route.route_id == route_id).one()
        return cls.from_route_orm(route, agency=agency, detailed=detailed, show_alerts=show_alerts)

