from __future__ import print_function
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
    
    Attributes
    ----------
    service: Gmail resource
        Gmail API resource with an Gmail user session opened.
    quota: int
        Gmail API quota units available for message extraction. Represents the
        remaining quota units available to carry out the extraction operations.
    init_time: float 
        Moment in which the second of operations begins.
    last_req_time: float
        Moment in which the last Gmail API request was made.
    quota_sec: int
        Remaining Gmail API quota units per second from init_time moment.
    """
    def __init__(self, service, quota):
        """
        Class constructor.

        Parameters
        ----------
        service: Gmail resource
            Gmail API resource with an Gmail user session opened.
        quota: int
            Gmail API quota units available for message extraction.

        Returns
        -------
        Constructed Extractor class.

        """
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

        Parameters
        ----------
        req_quota: int
            Quota units of the Gmail API request that has just been made.

        Returns
        -------
        None.

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

        Parameters
        ----------
        req_quota: int
            Quota units of the Gmail API request that is going to be made.

        Returns
        -------
        None.

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
        """
        Returns the minimum quota units needed to make a request of the resource.

        Returns
        -------
        int: minimum quota units needed to continue with extraction.

        """
        pass

    @abc.abstractmethod
    def get_list_key(self):
        """
        Returns the key of the dictionary given by the list request for
        accessing to the list of the resource.

        Returns
        -------
        str: key of the dictionary.

        """
        pass

    @abc.abstractmethod
    def get_list(self, nextPage):
        """
        Obtains a dictionary which includes a list of the resource.

        Parameters
        ----------
        nextPage : str
            Page token to retrieve a specific page of results in the list.

        Returns
        -------
        If successful, this method returns a response body with the following 
        structure:
        {
            String_with_resource_name: [
                Gmail API resource of the specific extractor
            ],
            "nextPageToken": string,
            "resultSizeEstimate": unsigned integer
        }

        """
        pass

    @abc.abstractmethod
    def get_resource(self, resId):
        """
        Obtains the Gmail API resource of the specific extractor.

        Parameters
        ----------
        resId : str
            Resource's identifier that we want to retrieve.

        Returns
        -------
        Gmail API resource (thread or message) depending on the specific
        extractor.

        """
        pass

    @abc.abstractmethod
    def extract_msgs_from_resource(self, res):
        """
        Obtains a list of extracted messages.

        Parameters
        ----------
        res : Gmail API resource
            Gmail API resource (threads or messages) the specific extractor.

        Returns
        -------
        A list of messages with the following structure:
        {
            'id' : string,
            'threadId' : string,
            'to' : [ string ]
            'depth' : int,               # How many messages precede it
            'date' : long,               # Epoch ms
            'subject' : string,
            'body' : string,
            'bodyBase64' : string,
            'charLength' : int
        }

        """
        pass

    def extract_sent_msg(self, cond_var, nmsg, msgs, nextPage = None):
        extracted = 0
        self.init_time = time()
        while (extracted < nmsg and self.quota >= self.min_qu()):
            msg_list = self.get_list(nextPage)

            lst_size = len(msg_list[self.get_list_key()])
            if (extracted + lst_size < nmsg):
                nextPage = msg_list['nextPageToken']

            msg_list = msg_list[self.get_list_key()]
            i = 0
            while (i < lst_size and self.quota >= self.min_qu()):
                # Obtains the resource (message or thread) with the given id
                res = self.get_resource(msg_list[i]['id'])
                extracted_msgs = self.extract_msgs_from_resource(res)
                # Inserts the messages in the shared resource
                cond_var.acquire()
                for m in extracted_msgs:
                    msgs.append(m)
                cond_var.notify()
                cond_var.release()

                i += 1
                extracted += 1

        if extracted < nmsg:
            return self.quota, nextPage
        else:
            return self.quota