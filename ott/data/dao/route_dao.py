from ott.utils.dao.base import BaseDao
from ott.utils import date_utils
from .alerts_dao import AlertsDao

from sqlalchemy.orm import object_session
from gtfsdb import Route
try: Route.make_geom_lazy()
except: pass

import logging
log = logging.getLogger(__file__)


class RouteListDao(BaseDao):
    """ List of RouteDao data objects ... both list and RouteDao content ready for marshaling into JSON
    """
    def __init__(self, routes):
        super(RouteListDao, self).__init__()
        self.routes = routes
        self.count = len(routes)

    @classmethod
    def active_routes(cls, session, agency_id=None, date=None):
        """
        find route list from gtfsdb based on input date (default is server date)
        todo: move this to Routes into gtfsdb
        todo: doesn't work if a schedule has a doughnut hole, and a route (short-term cancelled) is not be active for a period of time
        todo: use agency_id in query
        """
        # step 1: grab all routes
        routes = session.query(Route).order_by(Route.route_sort_order).all()

        # step 2: filter dates based on date
        ret_val = cls._filter_active_routes(routes, date)

        return ret_val

    @classmethod
    def _filter_active_routes(cls, routes, date=None):
        """ filter the list of gtfsdb routes from the database based on date
            todo: move this to Routes into gtfsdb
        """
        # import pdb; pdb.set_trace()
        ret_val = []

        # step 1: get a valid date
        date = date_utils.str_to_date(date)
        if date:
            for r in routes:
                if r:
                    # step 2a: filter based on begin and/or end dates
                    if r.start_date or r.end_date:
                        if r.start_date and r.end_date:
                            if r.start_date <= date <= r.end_date:
                                ret_val.append(r)
                        elif r.start_date and r.start_date <= date:
                            ret_val.append(r)
                        elif r.end_date and date <= r.end_date:
                            ret_val.append(r)
                    else:
                        # invalid Route. dates; can't determine active status, so just pass the route as 'active'
                        ret_val.append(r)
        else:
            # step 2b: if no good input (default) date, just assign pull all routes into ret_val
            ret_val = routes

        return ret_val

    @classmethod
    def route_list(cls, session, agency="TODO", detailed=False, show_alerts=False, show_geo=False):
        """ make a list of RouteDao objects by query to the database
        """
        ret_val = None
        log.info("query Route table")
        route_list = []
        routes = cls.active_routes(session)
        for r in routes:
            rte = RouteDao.from_route_orm(route=r, agency=agency, detailed=detailed, show_alerts=show_alerts, show_geo=show_geo)
            route_list.append(rte)

        ret_val = RouteListDao(route_list)
        return ret_val


class RouteDao(BaseDao):
    """ RouteDao data object ready for marshaling into JSON
    """
    def __init__(self, route, alerts, show_geo=False):
        super(RouteDao, self).__init__()
        self.copy(route, show_geo)
        self.set_alerts(alerts)

    def copy(self, r, show_geo):
        self.name = r.route_name
        self.route_id = r.route_id
        self.short_name = r.route_short_name
        self.sort_order = r.route_sort_order
        self.url = getattr(r, 'route_url', None)
        self.add_route_dirs(r)
        if show_geo:
            self.geom = self.orm_to_geojson(r)

    def add_route_dirs(self, route):
        """ add the direction names to route
        """
        # step 0: two direction name vars
        dir0 = None
        dir1 = None

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
    def from_route_orm(cls, route, agency="TODO", detailed=False, show_alerts=False, show_geo=False):
        alerts = []
        try:
            if show_alerts:
                alerts = AlertsDao.get_route_alerts(object_session(route), route.route_id)
        except Exception as e:
            log.warn(e)
        ret_val = RouteDao(route, alerts, show_geo)
        return ret_val

    @classmethod
    def from_route_id(cls, session, route_id, agency="TODO", detailed=False, show_alerts=False, show_geo=False):
        """ make a RouteDao from a route_id and session
        """
        log.info("query Route table")
        route = session.query(Route).filter(Route.route_id == route_id).one()
        return cls.from_route_orm(route, agency=agency, detailed=detailed, show_alerts=show_alerts, show_geo=show_geo)
