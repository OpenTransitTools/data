from sqlalchemy.orm import joinedload

from ott.utils.dao.base import BaseDao
from .route_dao import RouteDao

from gtfsdb import Stop, CurrentStops
from gtfsdb import RouteStop

from ott.utils import num_utils
from ott.utils import transit_utils

import logging
log = logging.getLogger(__file__)


class StopDao(BaseDao):
    """ Stop data object that is  ready for marshaling into JSON

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
    """
    def __init__(self, stop, amenities, routes, alerts=None, distance=0.0, order=0, date=None, show_geo=False):
        super(StopDao, self).__init__()

        # import pdb; pdb.set_trace()
        self.copy_basics(self.__dict__, stop, show_geo)
        self.routes = routes
        self.short_names = None
        self.distance = distance
        self.order = order
        self.set_alerts(alerts)
        self.set_amenities(amenities)
        self.set_date(date)

    @classmethod
    def copy_basics(cls, tgt, src, show_geo):
        tgt['stop_id'] = src.stop_id
        tgt['name'] = src.stop_name
        tgt['description'] = src.stop_desc
        tgt['url'] = getattr(src, 'stop_url', None)
        if src.direction == '' or src.direction == None:
            tgt['direction'] = ''
        else:
            tgt['direction'] = "{0}bound".format(src.direction.capitalize())
        tgt['position'] = src.position
        tgt['type'] = src.location_type
        tgt['lat'] = src.stop_lat
        tgt['lon'] = src.stop_lon
        if show_geo:
            tgt['geom'] = cls.orm_to_geojson(src)

    def find_route(self, route_id):
        """ @return: RouteDao from the list of routes
        """
        ret_val = None
        if route_id and self.routes:
            for r in self.routes:
                if route_id == r.route_id:
                    ret_val = r
                    break
        return ret_val

    def set_amenities(self, amenities):
        self.amenities = amenities
        if amenities and len(amenities) > 0:
            self.amenities = sorted(list(set(amenities)))  # sorted and distinct (set) list of attributes 
            self.has_amenities = True
        else:
            self.has_amenities = False

    def get_route_short_names(self, stop_orm):
        """ add an array of short names to this DAO
        """
        # step 1: create a short_names list if we haven't already
        if not self.short_names:
            self.short_names = []

            # step 2: use either route-dao list or find the active stops
            routes = self.routes
            if routes is None or len(routes) == 0:
                routes = RouteStop.active_unique_routes_at_stop(stop_orm.session, stop_id=stop_orm.stop_id)
                routes.sort(key=lambda x: x.route_sort_order, reverse=False)

            # step 3: build the short names list
            for r in routes:
                sn = {'route_id': r.route_id, 'route_short_name': transit_utils.make_short_name(r)}
                self.short_names.append(sn)

        return self.short_names

    @classmethod
    def make_short_names(cls, stop_orm):
        """
        get route sort names serving this stop
        :param stop_orm:
        :return list of short names:
        TODO: move to Stop in gtfsdb
        """
        ret_val = []
        routes = RouteStop.active_unique_routes_at_stop(stop_orm.session, stop_id=stop_orm.stop_id)
        routes.sort(key=lambda x: x.route_sort_order, reverse=False)
        for r in routes:
            sn = {'route_id': r.route_id, 'route_short_name': transit_utils.make_short_name(r)}
            ret_val.append(sn)
        return ret_val

    @classmethod
    def from_stop_orm(cls, stop_orm, distance=0.0, order=0, agency="TODO", detailed=False, show_geo=False, show_alerts=False, date=None):
        """ make a StopDao from a stop object and session

            note that certain pages only need the simple stop info ... so we can 
            avoid queries of detailed stop info (like routes hitting a stop, alerts, etc...)
        """
        ret_val = None

        amenities = []
        routes = []
        alerts = []

        # step 1: if we want full details on this stop, include features and amenities, etc...
        if detailed:

            # step 2: get list of stop amenities
            amenities = []
            for f in stop_orm.stop_features:
                if f and f.feature_name:
                    amenities.append(f.feature_name)

            # step 3a: get the routes for a stop
            route_stops = RouteStop.active_unique_routes_at_stop(stop_orm.session, stop_id=stop_orm.stop_id, date=date)
            for r in route_stops:
                rs = None

                # step 3b: build the route object for the stop's route (could be detailed and with alerts)
                try:
                    rs = RouteDao.from_route_orm(route=r, agency=agency, detailed=detailed, show_alerts=show_alerts)
                except Exception as e:
                    log.info(e)
                    # step 3c: we got an error above, so let's try to get minimal route information
                    try:
                        rs = RouteDao.from_route_orm(route=r)
                    except Exception as e:
                        log.info(e)
                        log.info("couldn't get route information")

                # step 3d: build the list of routes
                if rs:
                    routes.append(rs)
            routes.sort(key=lambda x: x.sort_order, reverse=False)

        # TODO: shut off, as TriMet doesn't use route alerts right now (and I can't afford more /q)
        #if show_alerts:
        #    alerts = AlertsDao.get_stop_alerts(object_session(stop), stop.stop_id)

        # step 4: query db for route ids serving this stop...
        ret_val = StopDao(stop_orm, amenities, routes, alerts, distance, order, date, show_geo)
        return ret_val

    @classmethod
    def query_orm_for_stop(cls, session, stop_id, detailed=False, agency=None):  # TODO clean up params (make sure detailed is not 3rd param in callers)
        """ simple utility for quering a stop from gtfsdb
        """
        ret_val = None
        try:
            log.info("query Stop for {}".format(stop_id))
            q = session.query(Stop)
            q = q.filter(Stop.stop_id == stop_id)
            # TODO q.filter(Stop.agency_id == agency_id)
            if detailed:
                q = q.options(joinedload("stop_features"))
            ret_val = q.one()
        except Exception as e:
            log.info(e)
        return ret_val

    @classmethod
    def from_stop_id(cls, session, stop_id, distance=0.0, agency="TODO", detailed=False, show_geo=False, show_alerts=False, date=None):
        """ make a StopDao from a stop_id and session ... and maybe templates
        """
        ret_val = None
        try:
            log.info("query Stop table")
            stop = cls.query_orm_for_stop(session, stop_id, detailed)
            ret_val = cls.from_stop_orm(stop_orm=stop, distance=distance, agency=agency, detailed=detailed, show_geo=show_geo, show_alerts=show_alerts, date=date)
        except Exception as e:
            log.info(e)

        return ret_val

    @classmethod
    def from_stop_params(cls, session, params):
        """ will make a stop based on values set in ott.utils.parse.StopParamParser
        """
        ret_val = cls.from_stop_id(session=session, stop_id=params.stop_id, agency=params.agency, detailed=params.detailed, show_geo=params.show_geo, show_alerts=params.alerts, date=params.date)
        return ret_val


class StopListDao(BaseDao):
    """ List of StopDao data objects ... both list and contents ready for marshaling into JSON
    """
    def __init__(self, stops, name=None):
        super(StopListDao, self).__init__()
        self.stops = stops
        self.count = len(stops)
        self.name = name

    @classmethod
    def from_routestops_orm(cls, route_stops, agency="TODO", detailed=False, show_geo=False, show_alerts=False, active_stops_only=True):
        """ make a StopListDao based on a route_stops object
        """
        ret_val = None
        if route_stops and len(route_stops) > 0:
            stops = []
            for rs in route_stops:
                if active_stops_only and not rs.stop.is_active:
                    continue
                stop = StopDao.from_stop_orm(stop_orm=rs.stop, order=rs.order, agency=agency, detailed=detailed, show_geo=show_geo, show_alerts=show_alerts)
                stops.append(stop)
            ret_val = StopListDao(stops)
        return ret_val

    @classmethod
    def query_nearest_stops(cls, session, geojson_point, radius=None, limit=10, is_active=True):
        """
        query gtfsdb for as-the-crow-flies nearest stops ... not accurate around barriers like rivers, highways, etc...
        :params db session, POINT(x,y), limit=10:
        """
        # import pdb; pdb.set_trace()

        # step 1: query database via geo routines for N of stops cloesst to the POINT
        #         note we grab 10 extra in the /Q, because some stops might not be active (no routes)
        #         thus we filter them below
        log.info("query gtfsdb Stop table")
        q = session.query(Stop)
        q = q.filter(Stop.location_type == 0)  # just stops (not stations or entrances to stations)
        # if radius and float(radius):
        #     q = q.filter-by distance todo: either here or below?
        q = q.order_by(Stop.geom.distance_centroid(geojson_point))
        q = q.limit(limit + 10)
        stop_list = q.all()

        # step 2: filter stops
        distance_filtered = False
        ret_val = []
        for s in stop_list:
            # step 2a: filter stops w/out any routes assigned (stop should have active routes)
            if is_active and len(s.routes) < 1:
                continue

            # step 2b: stop if we have enough stops to return
            if len(ret_val) >= limit:
                break

            # step 2c: radius / distance filter
            # todo: this not working right now (note len routes is filter above)
            # todo: should this be part of query see above
            if radius and len(s.routes) < 1:
                distance_filtered = True
                continue

            # step 2d: passed all filters, so add to our return list
            ret_val.append(s)

        # step 3: cleanup ... if we didn't get enough stops, maybe add some (non-active) stops back
        if not distance_filtered and len(ret_val) < limit:
            cls._add_back_stops(cls, stop_list, ret_val)

        return ret_val

    @classmethod
    def query_bbox_stops(cls, session, geojson_bbox, limit=1000, is_active=True):
        """
        query gtfsdb for as-the-crow-flies nearest stops ... not accurate around barriers like rivers, highways, etc...
        :params db session, POINT(x,y), limit=10:
        """
        # import pdb; pdb.set_trace()

        # step 1: query database via geo routines for stops within
        #         note we grab 10 extra in the /Q, because some stops might not be active (no routes)
        #         thus we filter them below
        log.info("query gtfsdb Stop table")
        q = session.query(Stop)
        q = q.filter(Stop.location_type == 0)  # just stops (not stations or entrances to stations)
        q = q.filter(Stop.geom.ST_Within(geojson_bbox))
        q = q.limit(limit)
        stop_list = q.all()

        # step 2: filter stops
        ret_val = []
        for s in stop_list:
            # step 2a: filter stops w/out any routes assigned (stop should have active routes)
            if is_active and len(s.routes) < 1:
                continue

            # step 2b: stop if we have enough stops to return
            if len(ret_val) >= limit:
                break

            # step 2c: passed all filters, so add to our return list
            ret_val.append(s)

        return ret_val

    @classmethod
    def _add_back_stops(cls, all_stop_list, filtered_list, limit=7):
        for s in all_stop_list:
            if len(filtered_list) >= limit:
                break

            if s not in filtered_list:
                filtered_list.append(s)

    @classmethod
    def nearest_stops(cls, session, geo_params):
        """ make a StopListDao based on a route_stops object
            @params: lon, lat, limit=10, name=None, agency="TODO", detailed=False):
        """
        # import pdb; pdb.set_trace()

        # step 1: make POINT(x,y) / get desired limit number of stops
        point = geo_params.to_point_srid()
        limit = int(geo_params.limit)

        # TODO replace step 2 with this below.... really, replace this with otp_client_py nearest stops
        # step 2: query for N of stops cloesst to the POINT
        # stops = cls.query_otp_nearest_stops(point, limit)

        # step 2: query database via geo routines for N of stops cloesst to the POINT
        #         note we grab 10 extra in the /Q, because some stops might not be active (no routes), thus we filter them below
        log.info("query Stop table")
        q = session.query(Stop)
        q = q.filter(Stop.location_type == 0)
        q = q.order_by(Stop.geom.distance_centroid(point))
        q = q.limit(limit + 10)
        stops_list = q

        # step 3a: loop thru nearest N stops
        stops = []
        for s in stops_list:
            # todo remove steps 3a and 3d ... see above
            # step 3a: make sure this stop has routes assigned
            if len(s.routes) < 1:
                continue

            # step 3b: calculate distance
            dist = num_utils.distance_mi(s.stop_lat, s.stop_lon, geo_params.lat, geo_params.lon)

            # step 3c: make stop...plus add stop route short name
            stop = StopDao.from_stop_orm(stop_orm=s, distance=dist, agency=geo_params.agency, detailed=geo_params.detailed)
            stop.get_route_short_names(stop_orm=s)
            stops.append(stop)

            # step 3d: stop if we have enough stops to return
            if len(stops) >= limit:
                break

        # step 4: sort list then return
        stops = cls.sort_list_by_distance(stops)
        ret_val = StopListDao(stops, name=geo_params.name)
        return ret_val

    @classmethod
    def sort_list_by_distance(cls, stop_list, order=True):
        """ sort a python list [] by distance, and assign order
        """

        # step 1: sort the list
        stop_list.sort(key=lambda x: x.distance, reverse=False)

        # step 2: assign order
        if order:
            for i, s in enumerate(stop_list):
                s.order = i+1

        return stop_list


class CurrentStopsListDao(StopListDao):
    """
    List of StopDao data objects ... directly from the CurrentStops table
    """
    def __init__(self, stops, name=None):
        super(CurrentStopListDao, self).__init__(stops, name)

    @classmethod
    def all_stops(cls, session, agency="TODO", detailed=False, show_alerts=False):
        #import pdb; pdb.set_trace()
        """
        make a StopListDao all stops...
        """
        ret_val = None
        q = session.query(CurrentStops)
        cstops = q.all()
        if cstops and len(cstops) > 0:
            stops = []
            for s in cstops:
                #stop = StopDao.from_stop_orm(stop_orm=rs.stop, order=rs.order, agency=agency, detailed=detailed, show_geo=show_geo, show_alerts=show_alerts)
                stop = s
                stops.append(stop)
            ret_val = StopListDao(stops)
        return ret_val
