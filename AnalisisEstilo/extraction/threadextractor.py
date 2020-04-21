# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 14:32:54 2019

@author: Carlos Moreno Morera
"""

from __future__ import print_function
from extractor import Extractor
import quotaunits as qu
import base64
from extractedmessage import ExtractedMessage

class ThreadExtractor(Extractor):
    """
    Implements Extractor class
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
        Constructed ThreadExtractor class.

        """
        super().__init__(service, quota)
        self.min_qu = qu.MIN_QUNITS_THRD
        self.list_key = 'threads'

    def get_list(self, nextPage):
        """
        Obtains a dictionary which includes a list of threads.

        Parameters
        ----------
        nextPage : str
            Page token to retrieve a specific page of results in the list.

        Returns
        -------
        If successful, this method returns a response body with the following 
        structure:
        {
            'threads' : [
                Gmail API users.threads resource
            ],
            "nextPageToken": string,
            "resultSizeEstimate": unsigned integer
        }

        """
        self.wait_for_request(qu.THREADS_LIST)
        t = self.service.users().threads()
        l = t.list(userId = 'me', labelIds = ['SENT'], pageToken = nextPage).execute()
        self.update_attributes(qu.THREADS_LIST)
        return l

    def get_resource(self, resId):
        """
        Obtains the Gmail API threads resource.

        Parameters
        ----------
        resId : str
            Thread resource's identifier that we want to retrieve.

        Returns
        -------
        Gmail API users.threads resource.

        """
        self.wait_for_request(qu.THREADS_GET)
        t = self.service.users().threads().get(id = resId, userId = 'me').execute()
        self.update_attributes(qu.THREADS_GET)
        return t

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
        depth = 0
        l_msgs = []
        for m in res['messages']:
            self.data_extractor.set_new_message(m)
            msg = ExtractedMessage()
            self.data_extractor.insert_metadata(msg)
            msg.depth = depth
    
            subject = self.data_extractor.get_subject()
            if subject is not None:
                msg.subject = subject
                
            msg.charLength = 0
    
            plain_text = self.data_extractor.get_plain_text()
            if plain_text is not None:
                msg.bodyBase64Plain = base64.urlsafe_b64encode(
                    plain_text.encode()).decode()
                msg.plainEncoding = self.data_extractor.get_plain_encod()
                msg.charLength = len(plain_text)
    
            html_text = self.data_extractor.get_html_text()
            if html_text is not None:
                msg.bodyBase64Html = base64.urlsafe_b64encode(
                    html_text.encode()).decode()
                if (plain_text is None):
                    p_text = self.html_converter.handle(html_text)
                    msg.bodyBase64Plain = base64.urlsafe_b64encode(
                        p_text.encode()).decode()
                    msg.charLength = len(p_text)
            l_msgs.append(msg)
            depth += 1
        return l_msgs
