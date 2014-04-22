import logging
log = logging.getLogger(__file__)

from sqlalchemy import and_

from .model import EntitySelector
from .model import Alert

'''
  https://github.com/mattwigway/gtfsrdb
  http://trimet.org/transweb/ws/V1/FeedSpecAlerts/appId/3819A6A38C72223198B560DF0/includeFuture/true

  bin/python ott/controller/database/gtfsrdb/gtfsrdb.py -d sqlite:///gtfsdb.db -a http://trimet.org/transweb/ws/V1/FeedSpecAlerts/appId/3819A6A38C72223198B560DF0/includeFuture/true -o -w 300
  
'''


def via_route_id(session, route_id, agency_id='TODO: NotUsed', stop_id='TODO: NotUsed', def_val=[]):
    ''' get array of alerts per route
    '''
    ret_val = def_val
    try:
        #ret_val = session.query(Alert).join(Alert.InformedEntities).filter(EntitySelector.route_id == route_id).all()
        log.info("Alerts via route: {0}".format(route_id))
        ret_val = session.query(EntitySelector).filter(EntitySelector.route_id == route_id).all()
    except Exception, e:
        log.warn(e)
    return ret_val


def via_stop_id(session, stop_id, agency_id='TODO: NotUsed', def_val=[]):
    ret_val = def_val
    try:
        log.info("Alerts via stop: {0}".format(stop_id))
        ret_val = session.query(EntitySelector).filter(EntitySelector.stop_id == stop_id).all()
    except Exception, e:
        log.warn(e)
    return ret_val

