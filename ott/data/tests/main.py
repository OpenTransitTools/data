import sys
from gtfsdb import scripts
from gtfsdb import Database
from gtfsdb import Stop, Route, RouteStop, Block
from ott.data.dao.route_dao import RouteDao
from ott.data.dao.stop_dao import StopDao
from ott.data.dao.stop_dao import StopListDao
from ott.data.dao.route_stop_dao import RouteStopDao
from ott.data.dao.route_stop_dao import RouteStopListDao


def routes(db):
    routes = Route.active_route_ids(db.session)
    for r in routes:
        print r

def routes_stops(db, r="100", d="1"):
    q = db.session.query(RouteStop).filter(
        RouteStop.route_id == r,
        RouteStop.direction_id == d,
    )
    q = q.order_by(RouteStop.order)
    route_stops = q.all()

    ## NOTE: two perf issues ... first is stop.is_active ... that does N table scans on the trip table
    #stops = StopListDao.from_routestops_orm(route_stops=route_stops, detailed=True, show_geo=False, active_stops_only=True)

    # Trip Table Scans
    for s in route_stops:
        print s.stop.is_active
        #print s.__dict__

def stops(db):
    stops = Stop.active_stop_ids(db.session)
    for s in stops:
        print s

def stops_from_blocks(db):
    stops = Block.active_stop_ids(db.session)
    for s in stops:
        print s

def db_queries(db):
    #import pdb; pdb.set_trace()
    print RouteDao.from_route_id(db.session, "1", show_geo=True)
    print StopDao.from_stop_id(db.session, "2", detailed=True, show_geo=True, show_alerts=True)
    print RouteStopDao.from_route_direction(db.session, "2", "0", show_geo=True)
    print RouteStopListDao.from_route(db.session, "1", show_geo=True)

    for s in db.session.query(Stop).limit(2):
        print s.stop_name
    for r in db.session.query(Route).limit(2):
        print r.route_name

def main(argv):
    args, kwargs = scripts.get_args()
    db = Database(**kwargs)

    #stops_from_blocks(db)
    routes_stops(db)

if __name__ == "__main__":
    main(sys.argv)
