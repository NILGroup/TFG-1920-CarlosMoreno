# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 14:32:54 2019

@author: Carlos Moreno Morera
"""

from __future__ import print_function
import quotaunits as qu
from messageextractor import MessageExtractor
from threadextractor import ThreadExtractor
import multiprocessing
import spacy
from preprocessor import Preprocessor
from typocorrector import TypoCorrector
from stylemeter import StyleMeter
import confanalyser as cfa

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
    msg_raw: list
        Shared resource wich is a list of extracted messages with the following
        structure:
        {
            'id' : string,
            'threadId' : string,
            'to' : [ string ],
            'cc' : [ string ],
            'bcc' : [ string ],
            'from' : string,
            'depth' : int,               # How many messages precede it
            'date' : long,               # Epoch ms
            'subject' : string,          # Optional
            'bodyPlain' : string,        # Optional
            'bodyHtml' : string,         # Optional
            'bodyBase64Plain' : string,  # Optional
            'bodyBase64Html' : string,   # Optional
            'plainEncoding' : string,    # Optional
            'charLength' : int           # Optional
        }
    msg_prep: list
        Shared resource wich is a list of preprocessed messages with the
        following structure:
            {
                'id' : string,
                'threadId' : string,
                'to' : [ string ],
                'cc' : [ string ],
                'bcc' : [ string ],
                'from' : string,
                'depth' : int,               # How many messages precede it
                'date' : long,               # Epoch ms
                'subject' : string,          # Optional
                'bodyPlain' : string,
                'bodyBase64Plain' : string,
                'bodyBase64Html' : string,   # Optional
                'plainEncoding' : string,    # Optional
                'charLength' : int
                'doc' : Spacy's Doc
                'sentences' : [
                    {
                        doc: Spacy's Doc of the sentence
                        words: [Spacy's Tokens]
                    }
                ]
            }
    msg_corrected: list
        Shared resource wich is a list of corrected messages (by correcting
        the typographic errors) with the following structure:
            {
                'id' : string,
                'threadId' : string,
                'to' : [ string ],
                'cc' : [ string ],
                'bcc' : [ string ],
                'from' : string,
                'depth' : int,               # How many messages precede it
                'date' : long,               # Epoch ms
                'subject' : string,          # Optional
                'bodyPlain' : string,
                'bodyBase64Plain' : string,
                'plainEncoding' : string,    # Optional
                'charLength' : int
                'doc' : Spacy's Doc
                'sentences' : [
                    {
                        doc: Spacy's Doc of the sentence
                        words: [Spacy's Tokens]
                    }
                ]
                'corrections' : [
                    {
                        'text' : string,
                        'is_punct' : boolean
                        'is_lpunct' : boolean       # Optional
                        'is_rpunct' : boolean       # Optional
                        'is_url' : boolean
                        'is_email' : boolean
                        'lemma' : string            # Optional
                        'is_stop' : boolean
                        'pos' : string              # Optional
                        'position' : int
                        'sentenceIndex' : int
                        'sentenceInit' : int
                    }
                ]
            }
    cv_raw: multiprocessing.Condition
        Conditional variable which is needed to access to the shared 
        resource (msg_raw).
    cv_prep: multiprocessing.Condition
        Conditional variable which is needed to access to the shared 
        resource (msg_prep).
    cv_corrected: multiprocessing.Condition
        Conditional variable which is needed to access to the shared 
        resource (msg_corrected).
    ext_fin: multiprocessing.Event
        Event which informs that the process in charge of the message 
        extraction has finished.
    prep_fin: multiprocessing.Event
        Event which informs that the process in charge of the message 
        preprocessing has finished.
    typo_fin: multiprocessing.Event
        Event which informs that the process in charge of the message 
        typographic correction has finished.
    nlp: Spacy model
        Spacy's trained model which will be used for analysing the message's
        text.
    preprocessor: Preprocessor
        Object which performs the task of preprocessing the extracted messages
        in order to being analysed then.
    typocorrector: TypoCorrector
        Object which performs the task of correcting typographic errors from
        preprocessed messages in order to being analysed then.
    nres: int
        Number of the resource that is going to be extracted (messages or threads).
    meter: StyleMeter
        Object which performs the task of measuring the writting style from
        corrected messages.
    
    """
    def __init__(self, service, quota = qu.QUOTA_UNITS_PER_DAY, ext_msg = None):
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
            Indicates whether there where a previous extraction and whether it
            extracts messages or threads. The default is None.

        Returns
        -------
        Constructed Analyser class.

        """
        self.service = service
        self.quota = quota
        
        if (self.quota > qu.LABELS_GET):
            self.extractor = None
            self.msg_raw = []
            self.msg_prep = []
            self.msg_corrected = []
            self.cv_raw = multiprocessing.Condition()
            self.cv_prep = multiprocessing.Condition()
            self.cv_corrected = multiprocessing.Condition()
            self.ext_fin = multiprocessing.Event()
            self.prep_fin = multiprocessing.Event()
            self.typo_fin = multiprocessing.Event()
            
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
                self.extractor = MessageExtractor(self.service, self.quota, 
                                                      self.msg_raw, self.cv_raw,
                                                      self.ext_fin)
            else:
                with open('log.txt', 'a') as f:
                    f.write('Thread extractor has been selected.\n')
                self.extractor = ThreadExtractor(self.service, self.quota, 
                                                     self.msg_raw, self.cv_raw,
                                                     self.ext_fin)
                self.nres = sent_lb['threadsTotal']
            
            self.nlp = spacy.load(cfa.SPACY_MODEL)
            self.preprocessor = Preprocessor(self.msg_raw, self.msg_prep, 
                                                 self.cv_raw, self.cv_prep,
                                                 self.ext_fin, self.prep_fin,
                                                 self.nlp)
            self.typocorrector = TypoCorrector(self.msg_prep, self.msg_corrected,
                                               self.cv_prep, self.cv_corrected,
                                               self.prep_fin, self.typo_fin,
                                               self.nlp)
            self.meter = StyleMeter(self.msg_corrected, self.cv_corrected,
                                    self.typo_fin)

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
    
    def analyse(self, user, nextPageToken = None, sign = None):
        """
        Analyses all the messages of the given user.
        
        Parameters
        ----------
        user: str
            Gmail user.
        nextPageToken: str, optional
            Token of the next page for extracting messages. The default is None.
        sign: str, optional
            Signature of the user in his emails. The default value is None.
            
        Returns
        -------
        None.
        
        """
        p_ext = multiprocessing.Process(target = self.extractor.extract_sent_msg,
                                        args = (self.nres, nextPageToken))
        p_ext.start()
        p_prep = multiprocessing.Process(target = self.preprocessor.star_preprocessing,
                                         args = (user, sign))
        p_prep.start()
        p_typo = multiprocessing.Process(target = self.typocorrector.correct_msgs,
                                         args = (user))
        p_typo.start()
        p_meter = multiprocessing.Process(target = self.meter.measure_style,
                                          args = (user))
        p_meter.start()
        
        proc = [p_ext, p_prep, p_typo, p_meter]
        for p in proc:
            p.join()
