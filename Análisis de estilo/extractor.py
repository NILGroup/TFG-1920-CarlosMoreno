# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 14:32:54 2019

@author: Carlos Moreno Morera
"""

from __future__ import print_function
import abc
import quotaunits as qu
from abc import ABC
from abc import ABCMeta
from time import time
from time import sleep
from dataextractor import DataExtractor
import html2text

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
    data_extractor: DataExtractor
        Class that allows us to extract the information from a message.
    min_qu: int (abstract attribute)
        Minimum quota units needed to make a request of the resource.
    list_key: str (abstract attribute)
        Key of the dictionary given by the list request for accessing to the
        list of the resource.
    msgs: list
        Shared resource wich is a list of messages with the following structure:
        {
            'id' : string,
            'threadId' : string,
            'to' : [ string ]
            'cc' : [ string ]
            'bcc' : [ string ]
            'depth' : int,               # How many messages precede it
            'date' : long,               # Epoch ms
            'subject' : string,
            'bodyPlain' : string,
            'bodyHtml' : string,
            'bodyBase64Plain' : string,
            'bodyBase64Html' : string,
            'charLength' : int
        }
    
    cond_var: multiprocessing.Condition
        Conditional variable which is needed to access to the shared 
        resource (msgs).
    
    """
    def __init__(self, service, quota, msgs, cv):
        """
        Class constructor.

        Parameters
        ----------
        service: Gmail resource
            Gmail API resource with an Gmail user session opened.
        quota: int
            Gmail API quota units available for message extraction.
        msgs: list
            List of information about extracted messages.
        cv: multiprocessing.Condition
            Conditional varable for accessing to msgs.

        Returns
        -------
        Constructed Extractor class.

        """
        __metaclass__ = ABCMeta
        self.service = service
        self.quota = quota
        self.quota_sec = qu.QUOTA_UNITS_PER_SECOND
        self.msgs = msgs
        self.cond_var = cv
        self.init_time = time()
        self.last_req_time = time()
        self.data_extractor = DataExtractor()
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_emphasis = True
        self.html_converter.ignore_links = True
        self.html_converter.ignore_images = True
        self.html_converter.ignore_tables = True

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
            'to' : [ string ],
            'cc' : [ string ],
            'bcc' : [ string ],
            'from' : string,
            'depth' : int,               # How many messages precede it
            'date' : long,               # Epoch ms
            'subject' : string,
            'bodyPlain' : string,
            'bodyHtml' : string,
            'bodyBase64Plain' : string,
            'bodyBase64Html' : string,
            'charLength' : int
        }

        """
        pass

    def extract_sent_msg(self, nmsg, nextPage = None):
        """
        Extracts all the sent messages by using the Gmail API.

        Parameters
        ----------
        nmsg: int
            Number of messages to be extracted.
        nextPage: str
            Page token to retrieve a specific page of results in the list.

        Returns
        -------
        (int, int, str): If all the messages were extracted, it returns the
        remaining quota units in first argument, number of extracted messages
        in sencond argument and None in third argument. In other case, the 
        third argument will be the page token where the last message
        was extracted.

        """
        extracted = 0
        self.init_time = time()
        actual_page = ''
        while (extracted < nmsg and self.quota >= self.min_qu):
            msg_list = self.get_list(nextPage)
            actual_page = nextPage

            lst_size = len(msg_list[self.list_key])
            if (extracted + lst_size < nmsg):
                nextPage = msg_list['nextPageToken']

            msg_list = msg_list[self.list_key]
            i = 0
            while (i < lst_size and self.quota >= self.min_qu):
                # Obtains the resource (message or thread) with the given id
                res = self.get_resource(msg_list[i]['id'])
                extracted_msgs = self.extract_msgs_from_resource(res)
                # Inserts the messages in the shared resource
                self.cond_var.acquire()
                for m in extracted_msgs:
                    self.msgs.append(m)
                self.cond_var.notify()
                self.cond_var.release()

                i += 1
                extracted += 1

        if extracted < nmsg:
            return self.quota, extracted, actual_page
        else:
            return self.quota, extracted