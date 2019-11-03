from extractor import Extractor
import quotaunits as qu

class MessageExtractor(Extractor):
    def __init__(self, service, quota):
        super().__init__(service, quota)

    def min_qu(self):
        return qu.MIN_QUNITS_MSG

    def get_list_key(self):
        return 'messages'

    def get_list(self, nextPage):
        self.wait_for_request(qu.MSG_LIST)
        m = self.service.user().messages()
        l = m.list(userId = 'me', labelIds = ['SENT'], pageToken = nextPage).execute()
        self.update_attributes(qu.MSG_LIST)
        return l

    def get_resource(self, resId):
        self.wait_for_request(qu.MSG_GET)
        m = self.service.user().messages().get(id = resId, userId = 'me').execute()
        self.update_attributes(qu.MSG_GET)
        return m