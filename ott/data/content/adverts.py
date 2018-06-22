from datetime import datetime
from datetime import timedelta

from ott.utils import object_utils
from ott.utils import json_utils
from ott.utils import html_utils

import logging
log = logging.getLogger(__file__)


class Adverts(object):
    """ Example content: http://trimet.org/map/adverts/
    """
    def __init__(self, advert_url, timeout_mins=30):
        """
        """
        log.info("create an instance of {0}".format(self.__class__.__name__))
        self.advert_url = advert_url
        if timeout_mins:
            self.avert_timeout = timeout_mins
        else:
            self.avert_timeout = 30
        self.last_update = datetime.now() - timedelta(minutes = (self.avert_timeout+10))
        self.safe_content = None
        self.content = {'rail': {}, 'bus': {}}
        self.update()

    def update(self):
        """ update content...
        """
        try:
            if datetime.now() - self.last_update > timedelta(minutes = self.avert_timeout):
                log.debug("updating the advert content")
                self.last_update = datetime.now()
                self.content['rail']['en'] = json_utils.stream_json(self.advert_url, extra_path='adverts_train.json')
                self.content['rail']['es'] = json_utils.stream_json(self.advert_url, extra_path='adverts_train_es.json')
                self.content['bus']['en']  = json_utils.stream_json(self.advert_url,  extra_path='adverts_bus.json')
                self.content['bus']['es']  = json_utils.stream_json(self.advert_url,  extra_path='adverts_bus_es.json')
                if self.content['rail']['en']:
                    self.safe_content = self.content['rail']['en']
        except Exception as e:
            log.warn("couldn't update the advert content: {}".format(e))

    def query(self, mode="rail", lang="en"):
        """ 
        """
        ret_val = self.safe_content
        try:
            self.update()
            m = mode if object_utils.has_content(mode) else 'rail'
            ret_val = self.content[m][lang]
        except Exception as e:
            log.warn("no advert content for mode={0}, lang={1}".format(mode, lang))
        return ret_val 

    def query_by_request(self, request, mode="rail", lang="en"):
        m = html_utils.get_first_param(request, 'mode',     mode)
        l = html_utils.get_first_param(request, '_LOCALE_', lang)
        log.debug("mode={0}, lang={1}".format(m, l))
        return self.query(m, l)
