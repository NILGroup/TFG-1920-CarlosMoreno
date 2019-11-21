# -*- coding: utf-8 -*-
"""
Created on Sun Nov 17 18:27:33 2019

@author: Carlos
"""

from __future__ import print_function

class Preprocessor:
    
    def __init__(self, raw_msgs, msgs, cv_raw, cv_msgs):
        self.raw = raw_msgs
        self.preprocessed = msgs
        self.cv_raw = cv_raw
        self.cv_msgs = cv_msgs
        
    def star_preprocessing(self):
        self.cv_raw.acquire()
        while (len(self.raw) == 0):
            self.cv_raw.wait()
        msg_raw = self.raw.pop()
        self.cv_raw.release()
        