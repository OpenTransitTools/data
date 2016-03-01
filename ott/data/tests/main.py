import sys
from gtfsdb import scripts
from gtfsdb import Database
from gtfsdb import Stop, Route, Block
from ott.data.dao.route_dao import RouteDao
from ott.data.dao.stop_dao import StopDao
from ott.data.dao.route_stop_dao import RouteStopDao
from ott.data.dao.route_stop_dao import RouteStopListDao


def routes():
    args, kwargs = scripts.get_args()
    db = Database(**kwargs)
    routes = Route.active_route_ids(db.session)
    for r in routes:
        print r

def stops():
    args, kwargs = scripts.get_args()
    db = Database(**kwargs)
    stops = Stop.active_stop_ids(db.session)
    for s in stops:
        print s

def stops_from_blocks():
    args, kwargs = scripts.get_args()
    db = Database(**kwargs)
    stops = Block.unique_stop_ids(db.session)
    for s in stops:
        print s

def db_queries(argv):
    args, kwargs = scripts.get_args()
    db = Database(**kwargs)

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
    stops_from_blocks()

if __name__ == "__main__":
    main(sys.argv)
