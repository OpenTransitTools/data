import datetime
import time
from urllib2 import urlopen

from . import model
from utils import get_translation
from utils import get_gtfs_db


def check_feed(fm):
    ''' Check the feed version
    '''
    if fm.header.gtfs_realtime_version != u'1.0' or fm.header.gtfs_realtime_version != u'1':
        print 'Warning: feed version has changed: found {0}, expected 1.0'.format(fm.header.gtfs_realtime_version)

def make_pretty_short_name(r):
    ''' override me ... I'm TriMet specific (e.g., MAX, WES)
    '''
    ret_val = None
    if r.route_short_name and len(r.route_short_name) > 0:
        ret_val = r.route_short_name
    elif r.route_long_name and len(r.route_long_name) > 0:
        nm = r.route_long_name
        if "MAX " in nm:
            ret_val = nm.replace(" Line", "")
        elif nm == "WES Commuter Rail":
            ret_val = "WES"
        else:
            ret_val = nm
    return ret_val


def add_short_names(opts, alert_orm, route_ids=[]):
    ''' add all the route_short_names (from gtfsdb) to the Alert record as a comman separated string
    '''
    gtfs_db = get_gtfs_db(opts.dsn, opts.schema)
    if gtfs_db:
        short_names = []
        try:
            #import pdb; pdb.set_trace()
            from gtfsdb import Route
            routes = gtfs_db.session.query(Route).filter(Route.route_id.in_(route_ids)).order_by(Route.route_sort_order)
            for r in routes.all():
                nm = make_pretty_short_name(r)
                if nm and nm not in short_names:
                    short_names.append(nm)
            alert_orm.route_short_names = ', '.join([str(x) for x in short_names])
        except Exception, e:
            pass


def make_alert(session, pb, opts):
    ''' will make a gtfsrdb Alert and add it to the session
    '''
    fm = pb.FeedMessage()
    check_feed(fm)
    fm.ParseFromString(urlopen(opts.alerts).read())

    now = datetime.datetime.now()
    now_secs = time.mktime(now.timetuple())

    print 'Adding %s alerts' % len(fm.entity)
    for entity in fm.entity:
        alert = entity.alert

        start = alert.active_period[0].start
        end = alert.active_period[0].end
        

        alert_orm = model.Alert(
            start = start,
            end = end,
            cause = alert.DESCRIPTOR.enum_types_by_name['Cause'].values_by_number[alert.cause].name,
            effect = alert.DESCRIPTOR.enum_types_by_name['Effect'].values_by_number[alert.effect].name,
            url = get_translation(alert.url, opts.lang),
            header_text = get_translation(alert.header_text, opts.lang),
            description_text = get_translation(alert.description_text, opts.lang)
        )

        session.add(alert_orm)
        for ie in alert.informed_entity:
            dbie = model.EntitySelector(
                    agency_id = ie.agency_id,
                    route_id = ie.route_id,
                    route_type = ie.route_type,
                    stop_id = ie.stop_id,
    
                    trip_id = ie.trip.trip_id,
                    trip_route_id = ie.trip.route_id,
                    trip_start_time = ie.trip.start_time,
                    trip_start_date = ie.trip.start_date)
            session.add(dbie)
            alert_orm.InformedEntities.append(dbie)

        # FXP ADDED: 
        ids = []
        for ie in alert.informed_entity:
            ids.append(ie.route_id)
        alert_orm.route_ids = ', '.join([str(x) for x in ids])
        add_short_names(opts, alert_orm, ids)

