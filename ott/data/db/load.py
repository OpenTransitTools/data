from sqlalchemy import engine_from_config
from pkg_resources import resource_filename
from gtfsdb import Database
from gtfsdb import Stop

from ott.data.dao.stop_response import StopResponse
from ott.data.dao.route_response import RouteListResponse

def get_model(db, model):
    return db.session.query(model)

def main():
    db = Database(url="sqlite:///gtfs.db")
    s  = StopResponse.from_stop_id('2', db.session)
    rl = RouteListResponse.route_list(db.session)
    print s
    print
    print rl
