from .response_base import ResponseBase
#from ott.controller.services.model.alerts_response import AlertsResponse

class RouteListResponse(ResponseBase):
    ''' List of RouteResponse data objects ... both list and RouteResponse content ready for marshaling into JSON
    '''
    def __init__(self, routes):
        self.routes = routes

class RouteResponse(ResponseBase):
    ''' RouteResponse data object ready for marshaling into JSON
    '''
    def __init__(self, route, stop=None, session=None):
        super(RouteResponse, self).__init__()
        self.copy(route)
        self.add_route_dirs(route)
        self.alerts = []
        #self.alerts = AlertsResponse.get_route_alerts(session, route.route_id)
        self.has_alerts = self.alerts and len(self.alerts) > 0

        # fill out templates
        #if stop:
        #    self.arrival_url = self.format_template_from_dict(stop, route.arrival_url)

    def old_copy(self, route):
        self.route_id = route.route_id
        self.name = route.rout_name
        self.short_name = route.short_name
        self.sort_order = route.sort_order
        self.route_url = route.route_url
        self.routelist_url = route.routelist_url
        self.arrival_url = route.arrival_url

    def copy(self, route):
        self.route_id = route.route_id
        self.name = route.route_long_name
        self.short_name = route.route_short_name
        #self.sort_order = route.sort_order
        #self.route_url = route.route_url
        #self.routelist_url = route.routelist_url
        #self.arrival_url = route.arrival_url

    def copy_dirs(self, dir0=None, dir1=None):
        self.direction_0 = dir0
        self.direction_1 = dir1

    def add_route_dirs(self, route):
        # step 0: two direction name vars
        dir0=None
        dir1=None

        # step 1: figure out what (if any) 'primary' direction names for this route exist in directions '0' and '1'
        try:
            for d in route.direction:
                if d.is_primary == True:
                    if d.direction_id == 0:
                        dir0 = d.direction_name
                    elif d.direction_id == 1:
                        dir1 = d.direction_name
        except:
            pass

        # step 2: assign direction names (or default null values) to route
        self.copy_dirs(dir0, dir1)


