

def stops(num, session):
    ''' measure the time of querying N number of stops, and how long it takes to show their 
        related attributes (e.g., routes, headsigns, stop times, etc...) 
    '''
    from gtfsdb import Stop
    from datetime import datetime
    import time

    out = "Starting query(Stop) @ {}\n\n".format(datetime.now())

    st = time.time()
    stops = session.query(Stop).limit(num)
    for i, s in enumerate(stops):
        out += "{} (Stop ID {}):\n=============================\n\n".format(s.stop_name, s.stop_id)

        out += "{}\nHeadsigns (Stop ID {}):\n".format(datetime.now(), s.stop_id)
        for h in s.headsigns:
                out += "{} - {}\n".format(h[1], h[0].route_short_name)

        out += "{}\n\n{}\nStop Times (Stop ID {}):\n".format(datetime.now(), datetime.now(), s.stop_id)
        if s.stop_times and len(s.stop_times) > 1:
            out += "from: {}, to:{}\n".format(s.stop_times[0].departure_time, s.stop_times[-1].departure_time)

        out += "{}\n\n{}\nRoutes (Stop ID {}):\n".format(datetime.now(), datetime.now(), s.stop_id)
        for r in s.routes:
            out += r.route_short_name
            out += "\n"
        out += "{}\n\n".format(datetime.now())
        if i >= num-1:
            break
    end = time.time()
    out = "Total time {:.3f} seconds (for {} stops)\n\n{}".format(end-st, num, out) 
    return out
