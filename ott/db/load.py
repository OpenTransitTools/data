from sqlalchemy import engine_from_config
from pkg_resources import resource_filename
from gtfsdb import Database
from gtfsdb import Stop

from ott.json.stop_response import StopResponse

def get_model(db, model):
    return db.session.query(model)

def main():
    db = Database(url="sqlite:///gtfs.db")
    s = StopResponse.from_stop_id('2', db.session)
    print s


