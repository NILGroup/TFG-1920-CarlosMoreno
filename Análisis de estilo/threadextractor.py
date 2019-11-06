from __future__ import print_function
from extractor import Extractor
import quotaunits as qu

class ThreadExtractor(Extractor):
    def __init__(self, service, quota):
        super().__init__(service, quota)

    def min_qu(self):
        return qu.MIN_QUNITS_THRD

    def get_list_key(self):
        return 'threads'

    def get_list(self, nextPage):
        self.wait_for_request(qu.THREADS_LIST)
        t = self.service.user().threads()
        l = t.list(userId = 'me', labelIds = ['SENT'], pageToken = nextPage).execute()
        self.update_attributes(qu.THREADS_LIST)
        return l

    def get_resource(self, resId):
        self.wait_for_request(qu.THREADS_GET)
        t = self.service.user().threads().get(id = resId, userId = 'me').execute()
        self.update_attributes(qu.THREADS_GET)
        return t