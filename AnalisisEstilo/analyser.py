# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 14:32:54 2019

@author: Carlos Moreno Morera
"""
from __future__ import print_function
import quotaunits as qu
from extraction.messageextractor import MessageExtractor
from extraction.threadextractor import ThreadExtractor
import confanalyser as cfa
import requests
from extraction.extractedmessage import ExtractedMessage
import json
from initdb import init_db

class Analyser:
    """
    The class Analyser performs the task of analysing all the messages of a
    user in order to obtain metrics which differentiate between the style
    writing of each person.
    
    Attributes
    ----------
    service: Gmail resource
        Gmail API resource with an Gmail user session opened.
    quota: int
        Gmail API quota units available for message extraction. Represents the
        remaining quota units available to carry out the extraction operations.
    extractor: Extractor
        Object which performs the task of extracting sent messages 
        or sent threads from the user by accessing Gmail API.
    typocorrector: TypoCorrector
        Object which performs the task of correcting typographic errors from
        preprocessed messages in order to being analysed then.
    nres: int
        Number of the resource that is going to be extracted (messages or threads).
    meter: StyleMeter
        Object which performs the task of measuring the writting style from
        corrected messages.
    
    """
    def __init__(self, service, quota = qu.QUOTA_UNITS_PER_DAY, ext_msg = None,
                 num_extracted = None):
        """
        Class constructor.

        Parameters
        ----------
        service : Gmail resource
            Gmail API resource with an Gmail user session opened.
        quota : int, optional
            Gmail API quota units available for message extraction. The default 
            is qu.QUOTA_UNITS_PER_DAY.
        ext_msg: bool, optional
            Indicates whether there were a previous extraction and whether it
            extracts messages or threads. The default is None.
        num_extracted: int, optional
            If it was an extraction before, it indicates the number of resources
            extracted last time. The default is None.

        Returns
        -------
        Constructed Analyser class.

        """
        self.service = service
        self.quota = quota
        
        if (self.quota > qu.LABELS_GET):
            self.extractor = None
            
            l = self.service.users().labels()
            sent_lb = l.get(userId = 'me', id = 'SENT').execute()
            self.nres = sent_lb['messagesTotal']
            self.quota -= qu.LABELS_GET

            cost_msg_ext = self.__get_res_cost(qu.MSG_LIST, sent_lb['messagesTotal'], 
                                               qu.MSG_GET)
            cost_thrd_ext = self.__get_res_cost(qu.THREADS_LIST, sent_lb['threadsTotal'], 
                                                qu.THREADS_GET)

            if (((ext_msg is None) and cost_msg_ext <= cost_thrd_ext) or ext_msg):
                with open('log.txt', 'a') as f:
                    f.write('Message extractor has been selected.\n')
                self.extractor = MessageExtractor(self.service, self.quota)
            else:
                with open('log.txt', 'a') as f:
                    f.write('Thread extractor has been selected.\n')
                self.extractor = ThreadExtractor(self.service, self.quota)
                self.nres = sent_lb['threadsTotal']
                
            if ext_msg is not None:
                self.nres -= num_extracted

    def __get_res_cost(self, listcost, numres, getcost):
        """
        Gets the cost of extracting a resource (message or thread).
        
        Parameters
        ----------
        listcost: int
            Cost of getting a list of the resource in quota units.
        numres: int
            Number of the resource that is going to be extracted.
        getcost: int
            Cost of getting a resource in quota units.
            
        Returns
        -------
        int: cost of extracting the resource.
        
        """
        return listcost * (numres // cfa.NUM_RESOURCE_PER_LIST + 1) + getcost * numres
    
    def analyse(self, nextPageToken = None, sign = None):
        """
        Analyses all the messages of the given user.
        
        Parameters
        ----------
        nextPageToken: str, optional
            Token of the next page for extracting messages. The default is None.
        sign: str, optional
            Signature of the user in his emails. The default value is None.
            
        Returns
        -------
        None.
        
        """
        init_db()
        self.quota, msg_ids, nextPage = self.extractor.extract_sent_msg(self.nres,
                                                                        nextPageToken)
        
        for ide in msg_ids:
            ext_msg = ExtractedMessage.objects(msg_id = ide).first().to_json()
            ext_msg = json.loads(ext_msg)
            response = requests.post(cfa.URL_PREP, json = {'message' : ext_msg,
                                                  'sign': sign})
            if response.status_code != 200:
                with open('logerror.txt', 'a') as f:
                    f.write(f"Error en el preprocesado de {ext_msg['_id']}.\n")