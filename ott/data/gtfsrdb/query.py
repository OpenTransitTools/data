import logging
log = logging.getLogger(__file__)

from sqlalchemy import and_

from .model import EntitySelector

'''
  https://github.com/mattwigway/gtfsrdb
  http://trimet.org/transweb/ws/V1/FeedSpecAlerts/appId/3819A6A38C72223198B560DF0/includeFuture/true

  bin/python ott/controller/database/gtfsrdb/gtfsrdb.py -d sqlite:///gtfsdb.db -a http://trimet.org/transweb/ws/V1/FeedSpecAlerts/appId/3819A6A38C72223198B560DF0/includeFuture/true -o -w 300
  
'''


db_has_alerts_tables = None
def okay_to_query(session, tables=['alerts', 'entity_selectors']):
    ''' IMPORTANT: have to make sure the GTRTFS alerts stuff exists before we start querying for data...
                   If we don't want check, and query non-existant tables, then the DB sessions get very 
                   unstable for our normal GTFS data queries...
    '''
    global db_has_alerts_tables

    if db_has_alerts_tables != True:
        #import pdb; pdb.set_trace()
        try:
            engine = session.get_bind()
            schema = EntitySelector.__table__.schema
            db_has_alerts_tables = True
            for t in tables:
                log.info("Checking to see if TABLE {0} EXISTS:".format(t))
                table_exists = engine.dialect.has_table(engine.connect(), t, schema=schema)
                if not table_exists:
                    db_has_alerts_tables = False
                    break
        except Exception, e:
            log.warn("ERROR WHEN CHECKING GTFSRT TABLE {0} EXISTS:".format(e))
            db_has_alerts_tables = False

    return db_has_alerts_tables


def via_route_id(session, route_id, agency_id='TODO: NotUsed', stop_id='TODO: NotUsed', def_val=[]):
    ''' get array of alerts per route
    '''
    ret_val = def_val
    try:
        if okay_to_query(session):
            log.info("Alerts via route: {0}".format(route_id))
            log.info("QUERY EntitySelector table")
            ret_val = session.query(EntitySelector).filter(EntitySelector.route_id == route_id).all()
    except Exception, e:
        log.warn(e)
    return ret_val


def via_stop_id(session, stop_id, agency_id='TODO: NotUsed', def_val=[]):
    ret_val = def_val
    try:
        if okay_to_query(session):
            log.info("Alerts via stop: {0}".format(stop_id))
            log.info("QUERY EntitySelector table")
            ret_val = session.query(EntitySelector).filter(EntitySelector.stop_id == stop_id).all()
    except Exception, e:
        log.warn(e)
    return ret_val

