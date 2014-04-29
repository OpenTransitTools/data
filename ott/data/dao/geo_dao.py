import logging
log = logging.getLogger(__file__)

from ott.utils.base_dao import BaseDao
from ott.utils import html_utils
from ott.utils import object_utils

class GeoListDao(BaseDao):
    def __init__(self, results):
        self.results = results

class GeoDao(BaseDao):
    def __init__(self, name, lat, lon, city, stop_id, type, type_name, score):
        log.debug("create an instance of {0}".format(self.__class__.__name__))
        self.name = html_utils.html_escape(name)
        self.city = html_utils.html_escape(city)
        self.lat  = html_utils.html_escape_num(lat)
        self.lon  = html_utils.html_escape_num(lon)
        self.stop_id = html_utils.html_escape_num(stop_id)
        self.type = type
        self.type_name = type_name
        self.score = score

    @classmethod
    def make_geo_response(cls, doc):
        name = html_utils.html_escape(doc['name'])
        city = object_utils.safe_dict_val(doc, 'city', '').title()
        lat  = doc['lat']
        lon  = doc['lon']
        stop_id = object_utils.safe_dict_val(doc, 'stop_id')
        type = doc['type']
        type_name = doc['type_name']
        score = doc['score']
        ret_val = GeoDao(name, lat, lon, city, stop_id, type, type_name, score)
        return ret_val

    @classmethod
    def make_geo(cls, doc):
        ret_val = None
        name = html_utils.html_escape(doc['name'])
        lat  = doc['lat']
        lon  = doc['lon']
        ret_val = "{0}::{1},{2}".format(name, lat, lon)
        return ret_val

    @classmethod
    def make_geo_plus_city(cls, doc):
        ret_val = cls.make_geo(doc)
        city = html_utils.html_escape(doc['city'])
        if city:
            ret_val = "{0}::{1}".format(ret_val, city)
        return ret_val

