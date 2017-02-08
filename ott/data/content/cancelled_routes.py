from .base import Base

from datetime import datetime
from datetime import timedelta
import logging
log = logging.getLogger(__file__)


class CancelledRoutes(Base):

    def __init__(self, url, timeout_mins=None):
        '''
        '''
        super(CancelledRoutes, self).__init__(url, timeout_mins)
