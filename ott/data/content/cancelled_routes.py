from datetime import datetime
from datetime import timedelta
import logging
log = logging.getLogger(__file__)

from ott.utils import json_utils

class CancelledRoutes(object):

    def __init__(self, url, timeout_mins=60):
        '''
        '''
        log.info("create an instance of {0}".format(self.__class__.__name__))
        self.url = url
        self.content = None
        self.timeout = 60
        if timeout_mins:
            self.timeout = timeout_mins

        self.last_update = datetime.now() - timedelta(minutes = (self.timeout+10))
        self.update()

    def update(self):
        try:
            if self.content is None or datetime.now() - self.last_update > timedelta(minutes = self.timeout):
                log.debug("updating the content")
                self.last_update = datetime.now()
                c = json_utils.stream_json(self.url)
                if c:
                    self.content = c
        except Exception, e:
            log.warn("couldn't update the fare content: {}".format(e))

    def query(self, def_val=None):
        ''' 
        '''
        #import pdb; pdb.set_trace()
        ret_val = def_val
        try:
            self.update()
            if self.content:
                ret_val = self.content
        except Exception, e:
            log.warn("content query error: {}".format(e))
        return ret_val

    def __str__(self, list_sep=","):
        ret_val = ""
        if self.content:
            if isinstance(self.content, (list, tuple)):
                for c in self.content:
                    if len(ret_val) > 0:
                        ret_val = ret_val + list_sep
                    ret_val = ret_val + str(c)
            elif isinstance(self.content, str):
                ret_val = self.content
            else:
                ret_val = str(self.content)
        return ret_val
