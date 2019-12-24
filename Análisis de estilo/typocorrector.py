# -*- coding: utf-8 -*-
"""
Created on Fri Dec 20 22:09:13 2019

@author: Carlos Moreno Morera
"""

from __future__ import print_function
import os
from csv import DictWriter

class TypoCorrector:
    
    def __init__(self, prep, corrected, prep_cv, cor_cv, prep_fin, typo_fin, nlp):
        self.prep = prep
        self.corrected = corrected
        self.prep_cv = prep_cv
        self.corrected_cv = cor_cv
        self.pre_fin = prep_fin
        self.typo_fin = typo_fin
        self.nlp = nlp
        
    def correct_msgs(self, user):
        if not os.path.exists(user + '/Preprocessing'):
            os.mkdir(user + '/Preprocessing')
        
        csv_columns = ['id', 'threadId', 'to', 'cc', 'bcc', 'from',
                       'depth', 'date', 'subject', 'bodyBase64Plain', 
                       'bodyBase64Html', 'plainEncoding', 'charLength']
        if not os.path.exists(user + '/Preprocessing/preprocessed.csv'):
            csvfile = open(user + '/Preprocessing/preprocessed.csv', 'w')
            writer = DictWriter(csvfile, fieldnames = csv_columns)
            writer.writeheader()
        else:
            csvfile = open(user + '/Preprocessing/preprocessed.csv', 'a')
            writer = DictWriter(csvfile, fieldnames = csv_columns)
        
        self.prep_cv.aquire()
        while (not(self.pre_fin.is_set()) or len(self.prep) > 0):
            while (len(self.prep) == 0 and not(self.pre_fin.is_set())):
                self.prep_cv.wait()
            if (len(self.prep) != 0):
                prep_msg = self.prep.pop()
            self.prep_cv.release()
            
            if (not(self.pre_fin.is_set())):
                msg_typo = {}
                                
                self.corrected_cv.acquire()
                self.corrected.append(msg_typo)
                self.corrected_cv.notify()
                self.corrected_cv.release()
                
                self.prep_cv.acquire()
        
        self.prep_cv.release()
        
        self.corrected_cv.acquire()
        self.typo_fin.set()
        self.corrected_cv.notify()
        self.corrected_cv.release()