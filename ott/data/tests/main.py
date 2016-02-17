import sys
from gtfsdb import scripts
from gtfsdb import Database
from gtfsdb import Stop, Route
from ott.data.dao.route_dao import RouteDao
from ott.data.dao.stop_dao import StopDao
#    stop_dao

def main(argv):
    args, kwargs = scripts.get_args()
    db = Database(**kwargs)

    #import pdb; pdb.set_trace()
    #print RouteDao.from_route_id(db.session, "1", show_geo=True)
    print StopDao.from_stop_id(db.session, "2", show_geo=True)

def x():
    for s in db.session.query(Stop).limit(2):
        print s.stop_name
    for r in db.session.query(Route).limit(2):
        print r.route_name


if __name__ == "__main__":
    main(sys.argv)