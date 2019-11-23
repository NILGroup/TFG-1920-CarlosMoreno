# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 14:32:54 2019

@author: Carlos Moreno Morera
"""

from __future__ import print_function
from extractor import Extractor
import quotaunits as qu
import base64

class MessageExtractor(Extractor):
    """
    Implements Extractor class
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
        Constructed MessageExtractor class.

        """
        super().__init__(service, quota, msgs, cv)
        self.min_qu = qu.MIN_QUNITS_MSG
        self.list_key = 'messages'

    def get_list(self, nextPage):
        """
        Obtains a dictionary which includes a list of messages.

        Parameters
        ----------
        nextPage : str
            Page token to retrieve a specific page of results in the list.

        Returns
        -------
        If successful, this method returns a response body with the following 
        structure:
        {
            'messages' : [
                Gmail API users.messages resource
            ],
            "nextPageToken": string,
            "resultSizeEstimate": unsigned integer
        }

        """
        self.wait_for_request(qu.MSG_LIST)
        m = self.service.users().messages()
        l = m.list(userId = 'me', labelIds = ['SENT'], pageToken = nextPage).execute()
        self.update_attributes(qu.MSG_LIST)
        return l

    def get_resource(self, resId):
        """
        Obtains the Gmail API messages resource.

        Parameters
        ----------
        resId : str
            Message resource's identifier that we want to retrieve.

        Returns
        -------
        Gmail API users.messages resource.

        """
        self.wait_for_request(qu.MSG_GET)
        m = self.service.users().messages()
        msg = m.get(id = resId, userId = 'me').execute()
        self.update_attributes(qu.MSG_GET)
        return msg
    
    def __count_num_ref(self, refer):
        """
        Counts the number of references which contains the references message header.
        
        Parameters
        ----------
        refer : str
            References message header.
            
        Returns
        -------
        int: number of references.
        
        """
        count = 0
        abierto = False
        for c in refer:
            if (abierto and c == '>'):
                abierto = False
                count += 1
            elif (not(abierto) and c == '<'):
                abierto  = True
        return count

    def extract_msgs_from_resource(self, res):
        """
        Obtains a list with the information of the given messages.

        Parameters
        ----------
        res : Gmail API users.messages resource
            Gmail API users.messages resource.

        Returns
        -------
        A list of messages (with an only element) with the following structure:
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
        self.data_extractor.set_new_message(res)
        metadata = self.data_extractor.get_dict()
        metadata['depth'] = 0

        subject = self.data_extractor.get_subject()
        if subject is not None:
            metadata['subject'] = subject
            
        refer = self.data_extractor.get_references()
        if refer is not None:
            metadata['depth'] = self.__count_num_ref(refer)
        else:
            metadata['depth'] = 0

        plain_text = self.data_extractor.get_plain_text()
        if plain_text is not None:
            metadata['bodyPlain'] = plain_text
            metadata['bodyBase64Plain'] = base64.urlsafe_b64encode(
                plain_text.encode()).decode()
            metadata['charLength'] = len(plain_text)

        html_text = self.data_extractor.get_html_text()
        if html_text is not None:
            metadata['bodyHtml'] = html_text
            metadata['bodyBase64Html'] = base64.urlsafe_b64encode(
                html_text.encode()).decode()
            if (plain_text is None):
                p_text = self.html_converter.handle(html_text)
                metadata['bodyPlain'] = p_text
                metadata['bodyBase64Plain'] = base64.urlsafe_b64encode(
                    p_text.encode()).decode()
                metadata['charLength'] = len(p_text)
        return [metadata]
