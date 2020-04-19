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
from html2text import HTML2Text
from messageinfo import MessageInfo

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
        self.data_extractor = DataExtractor()
        self.html_converter = HTML2Text()
        self.html_converter.ignore_emphasis = True
        self.html_converter.ignore_links = True
        self.html_converter.ignore_images = True
        self.html_converter.ignore_tables = True
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
        A list of MessageInfo objects.

        """
        pass

    def extract_sent_msg(self, nmsg, nextPage = None):
        """
        Extracts all the sent messages by using the Gmail API.

        Parameters
        ----------
        nmsg: int
            Number of messages or threads to be extracted.
        nextPage: str
            Page token to retrieve a specific page of results in the list.

        Returns
        -------
        quota: int
            Remaining quota units of Gmail API.
        msgs_ids: list
            List of all of extracted message's identifiers.
        actual_page: str
            Page token where the last message was extracted.

        """
        extracted = 0
        self.init_time = time()
        actual_page = ''
        msgs_ids = []
        while (extracted < nmsg and self.quota >= self.min_qu):
            msg_list = self.get_list(nextPage)
            actual_page = nextPage

            lst_size = len(msg_list[self.list_key])
            if (extracted + lst_size < nmsg):
                nextPage = msg_list['nextPageToken']

            msg_list = msg_list[self.list_key]
            i = 0
            while (i < lst_size and self.quota >= self.min_qu):
                # If the resource was not extracted before
                if not(MessageInfo.objects(msg_id = msg_list[i]['id']).first()):
                    # Obtains the resource (message or thread) with the given id
                    res = self.get_resource(msg_list[i]['id'])
                    extracted_msgs = self.extract_msgs_from_resource(res)
                   
                    # Save the message in database
                    for m in extracted_msgs:
                        m.save()
                        msgs_ids.append(m.msg_id)
                        
                    extracted += 1

                i += 1
        
        with open('log.txt', 'a') as f:
            f.write('\n\nEXTRACTION FINISHED:\n')
            f.write(f'Extracted resources: {extracted}\n')
            f.write(f'Remaining quota: {self.quota}\n')
                    
            if extracted < nmsg:
                f.write('Actual Page Token: ' + actual_page + '\n')
                f.write('Next Page Token: '+ nextPage + '\n')
                
        return self.quota, msgs_ids, actual_page