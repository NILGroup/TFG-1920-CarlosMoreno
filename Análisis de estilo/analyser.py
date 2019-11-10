from __future__ import print_function
import quotaunits as qu
import messageextractor as mex
import threadextractor as tex

NUM_RESOURCE_PER_LIST = 100

class Analyser:

    def __init__(self, service, quota = qu.QUOTA_UNITS_PER_DAY):
        self.service = service
        self.quota = quota
        self.extractor = None
        if (self.quota > qu.LABELS_GET):
            sent_lbl = self.service.users().labels().get(userId = 'me', id = 'SENT').execute()
            self.quota -= qu.LABELS_GET

            cost_msg_ext = self.__calculate_resource_cost(qu.THREADS_LIST,
                                            sent_lbl['messagesTotal'], qu.MSG_GET)
            cost_thrd_ext = self.__calculate_resource_cost(qu.THREADS_LIST,
                                            sent_lbl['threadsTotal'], qu.THREADS_GET)
            if (cost_msg_ext <= cost_thrd_ext):
                self.extractor = mex.MessageExtractor(self.service, self.quota)
            else:
                self.extractor = tex.ThreadExtractor(self.service, self.quota)

    def __calculate_resource_cost(self, listcost, numres, getcost):
        return listcost * (numres // NUM_RESOURCE_PER_LIST + 1) + getcost * numres
