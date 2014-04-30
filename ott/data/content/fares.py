from datetime import datetime
from datetime import timedelta
import logging
log = logging.getLogger(__file__)

class Fares(object):

    def __init__(self, fare_domain, fare_timeout_mins=30):
        '''
        '''
        self.domain = fare_domain
        self.fare_timeout = fare_timeout_mins
        log.info("create an instance of {0}".format(self.__class__.__name__))

    def update(self):
        try:
            #import pdb; pdb.set_trace()
            
            if datetime.now() - self.last_update > timedelta(minutes = self.fare_timeout):
                log.debug("updating the advert content")
        except:
            log.warn("couldn't update the advert")
 
    def query(self, mode="rail", lang="en"):
        ret_val = self.safe_content
        try:
            self.update()
        except:
            log.warn("no advert content for mode={0}, lang={1}".format(mode, lang))
        return ret_val 

    def query_by_request(self, request, mode="rail", lang="en"):
        return self.query(m, l)

