# -*- coding: utf-8 -*-
"""
Created on Sun Nov 17 18:27:33 2019

@author: Carlos
"""

from __future__ import print_function
from email_reply_parser import EmailReplyParser

class Preprocessor:
    
    def __init__(self, raw_msgs, msgs, cv_raw, cv_msgs):
        self.raw = raw_msgs
        self.preprocessed = msgs
        self.cv_raw = cv_raw
        self.cv_msgs = cv_msgs
        
    def __clean_decoded_text(self, text):
        """
        Removes soft break lines of the message body.

        Parameters
        ----------
        text: str
            Message body

        Returns
        -------
        str: Message body without soft break lines.
        """
        new_text = ""
        i = 0
        n = len(text)
        while i < n:
            if (text[i] == '\r' and (i + 1 < n) and text[i + 1] == '\n'):
                i += 2
                while((i + 1 < n) and text[i] == '\r' and text[i + 1] == '\n'):
                    new_text = new_text + text[i] + text[i + 1]
                    i += 2
            else:
                new_text += text[i]
                i += 1
    
        return new_text
        
    def star_preprocessing(self):
        self.cv_raw.acquire()
        while (len(self.raw) == 0):
            self.cv_raw.wait()
        msg_raw = self.raw.pop()
        self.cv_raw.release()
        
        if 'bodyPlain' in msg_raw:
            msg_prep = {}
            if msg_raw['depth'] > 0:
                msg_prep['bodyPlain'] = EmailReplyParser.parse_reply(
                        msg_raw['bodyPlain'])