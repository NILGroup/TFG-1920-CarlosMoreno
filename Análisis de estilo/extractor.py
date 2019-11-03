import abc
import quotaunits as qu
from abc import ABC
from abc import ABCMeta
from time import time
from time import sleep

class Extractor(ABC):
    """
    The Extractor abstract class performs the task of extracting sent messages 
    or sent threads (it will materialize in the daughters classes ) from the 
    user by accessing Gmail API.
    
    Parameters:
        service: Gmail API resource with an Gmail user session opened.
        quota (int): Gmail API quota units available for message extraction.

    Attributes:
        service: variable where we store service.
        quota (int): variable where we store quota. Represents the remaining
            quota units available to carry out the extraction operations.
        init_time (float): Moment in which the second of operations begins.
        last_req_time (float): Momento in which the last request was made.
        quota_sec (int): remaining Gmail API quota units per second from 
            init_time moment.
    """
    def __init__(self, service, quota):
        __metaclass__ = ABCMeta
        self.service = service
        self.quota = quota
        self.quota_sec = qu.QUOTA_UNITS_PER_SECOND
        self.init_time = time()
        self.last_req_time = time()

    def update_attributes(self, req_quota):
        """
        Update the quota, quota_sec and last_req_time attributes of this class
        after making a Gmail API request with the req_quota quota units.

        Parameters:
            req_quota (int): quota units of the Gmail API request that has just
                been made.
        """
        self.last_req_time = time()
        self.quota = self.quota - req_quota
        self.quota_sec = self.quota_sec - req_quota

    def wait_for_request(self, req_quota):
        """
        Avoid exceeding Gmail API quota units per second by waiting for the time
        needed to make the request with req_quota quota units. Besides this
        method updates the init_time attribute if from init_time until now more
        than a second has passed.

        Parameters:
            req_quota (int): quota units of the Gmail API request that is going
                to be made.
        """
        slept = False
        t_now = time()
        # If we are going to exceed the quota units per second in this last second
        # or the init_time attribute is not updated
        if ((t_now - self.init_time <= 1 and req_quota >= self.quota_sec)
            or (t_now - self.init_time > 1 and t_now - self.last_req_time <= 1)):
            slept = True
            sleep(1.1 - (t_now - self.last_req_time))

        if slept or (t_now - self.init_time > 1):
            self.quota_sec = qu.QUOTA_UNITS_PER_SECOND
            self.init_time = time()
            self.last_req_time = time()

    @abc.abstractmethod
    def min_qu(self):
        pass

    @abc.abstractmethod
    def get_list_key(self):
        pass

    @abc.abstractmethod
    def get_list(self, nextPage):
        pass

    @abc.abstractmethod
    def get_resource(self, resId):
        pass

    def extract_sent_msg(self, cond_var, nmsg, msgs):
        extracted = 0
        nextPage = None
        self.init_time = time()
        while (extracted < nmsg and self.quota >= self.min_qu()):
            msg_list = self.get_list(nextPage)

            lst_size = len(msg_list[self.get_list_key()])
            if (extracted + lst_size < nmsg):
                nextPage = msg_list['nextPageToken']

            msg_list = msg_list[self.get_list_key()]
            i = 0
            while (i < lst_size and self.quota >= self.min_qu()):
                #Obtains the resource (message or thread) with the given id
                res = self.get_resource(msg_list[i]['id'])


        #Si se queda a medias guardar estado en un archivo
        #Utilizar variables de condición
        #https://docs.python.org/3.5/library/threading.html#threading.Condition