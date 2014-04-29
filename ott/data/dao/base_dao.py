import logging
log = logging.getLogger(__file__)

import simplejson as json
import calendar, datetime

registry = SerializerRegistry()

@registry.add
class BaseDao(object):
    def __init__(self):
        self.status_code = '200'
        self.status_message = None
        self.has_errors = False

    def __repr__(self):
        return str(self.__dict__)

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, dct):
        return cls(**dct)

    @classmethod
    def obj_to_json(cls, obj, pretty=False):
        if pretty:
            ret_val = json.dumps(obj, default=registry.default, indent=4, sort_keys=True)
        else:
            ret_val = json.dumps(obj, default=registry.default)
        return ret_val

    def to_json(self, pretty=False):
        return self.obj_to_json(self, pretty)

    def from_json(self, str):
        return json.loads(str, object_hook=registry.object_hook)

    @classmethod
    def format_template_from_dict(cls, dict, template):
        ret_val = template
        try:
            ret_val = template.format(**dict)
        except:
            pass
        return ret_val

    def set_alerts(self, alerts):
        self.alerts = alerts
        if self.alerts and len(self.alerts) > 0:
            self.has_alerts = True
        else:
            self.has_alerts = False


class DatabaseNotFound(BaseDao):
    def __init__(self):
        super(DatabaseNotFound, self).__init__()
        self.status_code = '404'
        self.status_message = 'Data Not Found'
        self.has_errors = True


class ServerError(BaseDao):
    def __init__(self):
        super(ServerError, self).__init__()
        self.status_code = '500'
        self.status_message = 'Internal Server Error'
        self.has_errors = True


class SerializerRegistry(object):
    ''' @see: http://stackoverflow.com/questions/4821940/how-to-make-simplejson-serializable-class
        this class will help serialize abitrary python objects into JSON (along with date / datetime handelling)
    '''
    def __init__(self):
        self._classes = {}

    def add(self, cls):
        self._classes[cls.__module__, cls.__name__] = cls
        return cls

    def object_hook(self, dct):
        module, cls_name = dct.pop('__type__', (None, None))
        if cls_name is not None:
            return self._classes[module, cls_name].from_dict(dct)
        else:
            return dct

    def default(self, obj):
        if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date):
            # simple / stupid handling of date and datetime object serialization
            return str(obj)
        else:
            dct = obj.to_dict()
            dct['__type__'] = [type(obj).__module__, type(obj).__name__]
            return dct
