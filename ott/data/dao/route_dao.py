import logging
log = logging.getLogger(__file__)

from .base_dao import BaseDao
from .alerts_dao import AlertsDao


class RouteListDao(BaseDao):
    ''' List of RouteDao data objects ... both list and RouteDao content ready for marshaling into JSON
    '''
    def __init__(self, routes):
        super(RouteListDao, self).__init__()
        self.routes = routes

    @classmethod
    def route_list(cls, session):
        ''' make a list of RouteDao objects by query to the database
        '''
        ### TODO: list of BANNED ROUTES ...
        from gtfsdb.model.route import Route
        route_list = [] 
        routes = session.query(Route).order_by(Route.route_sort_order)
        for r in routes:
            rte = RouteDao(route=r, session=session)
            route_list.append(rte)

        ret_val = RouteListDao(route_list)
        return ret_val


class RouteDao(BaseDao):
    ''' RouteDao data object ready for marshaling into JSON
    '''
    def __init__(self, route, session=None, stop=None):
        super(RouteDao, self).__init__()
        #import pdb; pdb.set_trace()
        self.copy(route)
        self.add_route_dirs(route)
        self.alerts = []
        self.alerts = AlertsDao.get_route_alerts(session, route.route_id)
        self.has_alerts = self.alerts and len(self.alerts) > 0


    def copy(self, r):
        self.name = r.route_name
        self.route_id = r.route_id
        self.short_name = r.route_short_name
        self.sort_order = r.route_sort_order


    def old_copy(self, route):
        # fill out templates
        #if stop:
        #    self.arrival_url = self.format_template_from_dict(stop, route.arrival_url)

        self.route_id = route.route_id
        self.name = route.route_name
        self.short_name = route.short_name
        self.sort_order = route.sort_order
        self.route_url = route.route_url
        self.routelist_url = route.routelist_url
        self.arrival_url = route.arrival_url


    def copy_dirs(self, dir0=None, dir1=None):
        self.direction_0 = dir0
        self.direction_1 = dir1

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


    @classmethod
    def from_route_id(cls, route_id, session, agency="TODO"):
        ''' make a RouteDao from a route_id and session
        '''
        #import pdb; pdb.set_trace()
        from gtfsdb import Route
        r = session.query(Route).filter(Route.route_id == route_id).one()
        ret_val = RouteDao(r, session)
        return ret_val
