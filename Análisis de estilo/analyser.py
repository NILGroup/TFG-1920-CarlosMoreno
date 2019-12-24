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
import confanalyser as cfa

class Analyser:

    def __init__(self, service, quota = qu.QUOTA_UNITS_PER_DAY):
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
            
            l = self.service.users().labels()
            sent_lb = l.get(userId = 'me', id = 'SENT').execute()
            self.quota -= qu.LABELS_GET

            cost_msg_ext = self.__get_res_cost(qu.MSG_LIST, sent_lb['messagesTotal'], 
                                               qu.MSG_GET)
            cost_thrd_ext = self.__get_res_cost(qu.THREADS_LIST, sent_lb['threadsTotal'], 
                                                qu.THREADS_GET)

            if (cost_msg_ext <= cost_thrd_ext):
                self.extractor = MessageExtractor(self.service, self.quota, 
                                                      self.msg_raw, self.cv_raw,
                                                      self.ext_fin)
            else:
                self.extractor = ThreadExtractor(self.service, self.quota, 
                                                     self.msg_raw, self.cv_raw,
                                                     self.ext_fin)
            self.nlp = spacy.load(cfa.SPACY_MODEL)
            self.preprocessor = Preprocessor(self.msg_raw, self.msg_prep, 
                                                 self.cv_raw, self.cv_prep,
                                                 self.ext_fin, self.prep_fin,
                                                 self.nlp)

    def __get_res_cost(self, listcost, numres, getcost):
        return listcost * (numres // cfa.NUM_RESOURCE_PER_LIST + 1) + getcost * numres
