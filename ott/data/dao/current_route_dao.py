from ott.utils import date_utils
from .alerts_dao import AlertsDao
from .route_dao import RouteListDao

from sqlalchemy.orm import object_session
from gtfsdb import CurrentRoutes

import logging
log = logging.getLogger(__file__)


class CurrentRoutesListDao(RouteListDao):
    """ List of RouteDao data objects ... both list and RouteDao content ready for marshaling into JSON
    """
    def __init__(self, routes):
        super(CurrentRoutesListDao, self).__init__(routes)


    @classmethod
    def active_routes(cls, session, agency_id=None, date=None):
        """
        find route list from gtfsdb based on input date (default is server date)
        """
        croutes = session.query(CurrentRoutes).order_by(CurrentRoutes.route_sort_order).all()


    @classmethod
    def route_list(cls, session, agency="TODO", detailed=False, show_alerts=False, show_geo=False):
        """ make a list of RouteDao objects by query to the database
        """
        ret_val = None
        log.info("query CurrentRoute table")
        route_list = []
        routes = cls.active_routes(session)
        for r in routes:
            rte = CurrentRouteDao.from_route_orm(route=r, agency=agency, detailed=detailed, show_alerts=show_alerts, show_geo=show_geo)
            route_list.append(rte)

        ret_val = RouteListDao(route_list)
        return ret_val


class CurrentRouteDao(BaseDao):
    """ RouteDao data object ready for marshaling into JSON
    """
    def __init__(self, route, alerts, show_geo=False):
        super(CurrentRouteDao, self).__init__()
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
