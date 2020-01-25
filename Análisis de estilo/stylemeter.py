# -*- coding: utf-8 -*-
"""
Created on Thu Jan 23 16:17:23 2020

@author: Carlos Moreno Morera
"""

from __future__ import print_function
import os
from csv import DictWriter
import confstyle as cfs

class StyleMeter:
    
    def __init__(self, corrected, cor_cv, typo_fin):
        """
        Class constructor.

        Parameters
        ----------
        corrected : list
            List of preprocessed messages whose typographical errors have been 
            corrected.
        cor_cv : multiprocessing.Condition
            Conditional variable for accessing to corrected.
        typo_fin : multiprocessing.Event
            Event which informs whether or not the typographic correction of messages 
            has finished.

        Returns
        -------
        Constructed StyleMeter class.

        """
        self.corrected = corrected
        self.cor_cv = cor_cv
        self.typo_fin = typo_fin
        
    def __initialize_metrics(self, metrics, numSentences):
        metrics['numStopWords'] = 0
        # Number of adverbs
        metrics['ADV'] = 0
        metrics['VERB'] = 0
        metrics['ADJ'] = 0
        # Number of prepositions
        metrics['ADP'] = 0
        metrics['NOUN'] = 0
        metrics['PRON'] = 0
        metrics['DET'] = 0
        metrics['CONJ'] = 0
        
        metrics['numCommas'] = 0
        metrics['numDots'] = 0
        metrics['numSemiColon'] = 0
        metrics['num3Dots'] = 0
        metrics['numBrackets'] = 0
        
        metrics['wordLength'] = {}
        metrics['charLength'] = 0
        
        met_sents = metrics.copy()
        
        metrics['sentLength'] = {}
        # Creates a dictionary of information for each sentence
        metrics['metricsSentences'] = [met_sents for i in range(numSentences)]
        
    def __calculate_metrics(self, metrics, cor_msg, doc):
        self.__initialize_metrics(metrics, len(cor_msg['sentences']))
        
        words = {}
        
        metrics['msgLength'] = len(doc)
        metrics['charLength'] = cor_msg['charLength']
        
    def measure_style(self, user):
        if not os.path.exists(user + '/TypoCorrection'):
            os.mkdir(user + '/TypoCorrection')
            
        if not os.path.exists(user + '/TypoCorrection/typocorrected.csv'):
            csvfile = open(user + '/TypoCorrection/typocorrected', 'w')
            writer = DictWriter(csvfile, fieldnames = cfs.CSV_COL)
            writer.writeheader()
        else:
            csvfile = open(user + '/TypoCorrection/typocorrected', 'a')
            writer = DictWriter(csvfile, fieldnames = cfs.CSV_COL)
            
        self.cor_cv.acquire()
        while (not(self.typo_fin.is_set()) or len(self.corrected) > 0):
            extracted = False
            while (len(self.corrected) == 0 and not(self.typo_fin.is_set())):
                self.cor_cv.wait()
            if (len(self.corrected) > 0):
                cor_msg = self.corrected.pop()
                extracted = True
            self.cor_cv.release()
            
            if extracted:
                metrics = {}
                bodyMsg = cor_msg.pop('bodyPlain')
                doc = cor_msg.pop('doc')
                self.__calculate_metrics(metrics, cor_msg, doc)
                
            self.cor_cv.acquire()
        
        self.cor_cv.release()