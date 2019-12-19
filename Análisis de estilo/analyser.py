# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 14:32:54 2019

@author: Carlos Moreno Morera
"""

from __future__ import print_function
import quotaunits as qu
import messageextractor as mex
import threadextractor as tex
import multiprocessing
import spacy
import preprocessor as prp

NUM_RESOURCE_PER_LIST = 100

class Analyser:

    def __init__(self, service, quota = qu.QUOTA_UNITS_PER_DAY):
        self.service = service
        self.quota = quota
        self.extractor = None
        self.msg_raw = []
        self.msg_prep = []
        self.cv_raw = multiprocessing.Condition()
        self.cv_prep = multiprocessing.Condition()
        self.ext_fin = multiprocessing.Event()
        if (self.quota > qu.LABELS_GET):
            sent_lbl = self.service.users().labels().get(userId = 'me', id = 'SENT').execute()
            self.quota -= qu.LABELS_GET

            self.num_msg = sent_lbl['messagesTotal']
            self.num_thrd = sent_lbl['threadsTotal']

            cost_msg_ext = self.__get_res_cost(qu.MSG_LIST, self.num_msg, qu.MSG_GET)
            cost_thrd_ext = self.__get_res_cost(qu.THREADS_LIST, self.num_thrd, qu.THREADS_GET)

            if (cost_msg_ext <= cost_thrd_ext):
                self.extractor = mex.MessageExtractor(self.service, self.quota, self.msg_raw, self.cv_raw)
            else:
                self.extractor = tex.ThreadExtractor(self.service, self.quota, self.msg_raw, self.cv_raw)
            self.nlp = spacy.load("es_core_news_md")
            self.preprocessor = prp.Preprocessor(self.msg_raw, self.msg_prep, self.cv_raw, self.cv_prep,
                                                 self.ext_fin, self.nlp)

    def __get_res_cost(self, listcost, numres, getcost):
        return listcost * (numres // NUM_RESOURCE_PER_LIST + 1) + getcost * numres
