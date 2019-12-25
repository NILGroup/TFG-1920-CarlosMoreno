# -*- coding: utf-8 -*-
"""
Created on Fri Dec 20 22:09:13 2019

@author: Carlos Moreno Morera
"""

from __future__ import print_function
import os
import json
from csv import DictWriter

class TypoCorrector:
    
    def __init__(self, prep, corrected, prep_cv, cor_cv, prep_fin, typo_fin, nlp):
        self.prep = prep
        self.corrected = corrected
        self.prep_cv = prep_cv
        self.corrected_cv = cor_cv
        self.pre_fin = prep_fin
        self.typo_fin = typo_fin
        self.__load_words_oov()
        self.nlp = nlp
        
    def __load_words_oov(self):
        """
        Loads the words which are considered out of vocabulary by the spacy
        model and they are correctly written.

        Returns
        -------
        None.

        """
        if not os.path.exists('oov.json'):
            self.oov = {}
        else:
            with open('oov.json', 'r') as fp:
                self.oov = json.load(fp)
                
    def __save_words_oov(self):
        """
        Saves the words which are considered out of vocabulary by the spacy
        model and they are correctly written.

        Returns
        -------
        None.

        """
        with open('oov.json', 'w') as fp:
            json.dump(self.oov, fp)
            
    def __is_it_typo(self):
        """
        Asks the user if the word previously printed is a typographic error.
        
        Returns
        -------
        bool: true if it is a real typographic error and false if it is not.
        """
        print('\nIs it a real typographic error? [y/n] ')
        answ = input()
        while(not answ in {'y', 'n'}):
            print('Please write "y" or "n" to answer the question.\n')
            print('Is it a real typographic error? [y/n] ')
            answ = input()
            
        return answ == 'y'
            
    def __req_token_correction(self, ind, msg_typo):
        print(f'Typographic error: {msg_typo["doc"][ind].text}\n')
        print('Body message:\n\n')
        print(msg_typo['bodyPlain'])
        
        if (self.__is_it_typo()):
            print('Possible solutions:\n')
            print('1.- Remove word.\n')
            print('2.- Rewrite word.\n')
        
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
            extracted = False
            while (len(self.prep) == 0 and not(self.pre_fin.is_set())):
                self.prep_cv.wait()
            if (len(self.prep) > 0):
                prep_msg = self.prep.pop()
                extracted = True
            self.prep_cv.release()
            
            # If the body is not an empty string
            if (extracted and prep_msg['bodyPlain']):
                msg_typo = {}
                
                msg_typo['bodyPlain'] = prep_msg.pop('bodyPlain')
                msg_typo['doc'] = prep_msg.pop('doc')
                i = 0
                while i < len(msg_typo['doc']):
                    if msg_typo['doc'][i].is_oov:
                        i = self.__req_token_correction(i, msg_typo)
                    i += 1
                                
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
        
        csvfile.close()
        self.__save_words_oov()