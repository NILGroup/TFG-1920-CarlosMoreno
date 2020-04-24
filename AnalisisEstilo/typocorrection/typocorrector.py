# -*- coding: utf-8 -*-
"""
Created on Fri Dec 20 22:09:13 2019

@author: Carlos Moreno Morera
"""

from __future__ import print_function
import os
import json
import base64
from mytoken import MyToken

class TypoCorrector:
    """
    TypoCorrector class performs the task of correcting the typographic errors
    of the messages.
    
    Attributes
    ----------
    nlp: Spacy model
        Spacy's trained model which will be used for correcting typographic errors.
    oov: dict
        Dictionary where tokens out of vocabulary are stored in order to use
        them if they appears later in the correction. It has the following
        structure:
            {
            <token.text> : <MyToken class>
            }
            
    """
    
    def __init__(self, nlp):
        """
        Class constructor.

        Parameters
        ----------
        nlp : spacy model
            Spacy's trained model which will be used to processed.

        Returns
        -------
        Constructed TypoCorrector class.

        """
        self.oov = {}
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
        if os.path.exists('oov.json'):
            with open('oov.json', 'r') as fp:
                d = json.load(fp)
            for key in d:
                w = d[key]
                tok = MyToken(w['text'], w['punct'], w['rpunct'], w['lpunct'], 
                              w['url'], w['email'], w['lemma'], w['stop'], w['pos'],
                              w['bracket'])
                self.oov[key] = tok
                
    def __save_words_oov(self):
        """
        Saves the words which are considered out of vocabulary by the spacy
        model and they are correctly written.

        Returns
        -------
        None.

        """
        d = {}
        for key in self.oov:
            t = self.oov[key]
            d[key] = {'text' : t.text, 'punct': t.is_punct, 'rpunct' : t.is_right_punct,
                      'lpunct' : t.is_left_punct, 'url' : t.like_url,
                      'email' : t.like_email, 'lemma' : t.lemma_, 'stop' : t.is_stop,
                      'pos' : t.pos_, 'bracket' : t.is_bracket}
            
        with open('oov.json', 'w') as fp:
            json.dump(d, fp)
            
    def __get_structured_text(self, typo):
        """
        Adds to the typo dictionary a key 'doc', whose value will correspond with
        the Spacy's Doc of the body of the message, and a key 'sentences', whose
        value will have the next structure:
            [
                {
                    doc: Spacy's Doc of the sentence
                    words: [Spacy's Tokens]
                }
            ]
        Parameters
        ----------
        typo : dict
            Dictionary of the preprocessed message.
        Returns
        -------
        None.
        """
        typo['doc'] = self.nlp(typo['bodyPlain'])
        sentences = [s.text for s in typo['doc'].sents]
        typo['sentences'] = []

        for s in sentences:
            typo['sentences'].append({})
            typo['sentences'][-1]['doc'] = self.nlp(s)
            typo['sentences'][-1]['words'] = [t for t in 
                                                typo['sentences'][-1]['doc']]
            
    def __is_there_errors(self, tok):
        return tok.pos_ != 'SPACE' and tok.is_oov
    
    def __copy_data(self, prep_msg, msg_typo):
        """
        Copies the data from the preprocessed message to the message with the
        typographic errors corrected.
        
        Parameters
        ----------
        prep_msg: dict
            Dictionary which represents the preprocessed message. It has the
            next structure:
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
                    'bodyBase64Plain' : string,
                    'bodyBase64Html' : string,   # Optional
                    'plainEncoding' : string,    # Optional
                    'charLength' : int
                    'sentences' : [ [ string ] ]
                    ]
                }
        msg_typo: dict
            Dictionary where the data is going to be copied.
            
        Returns
        -------
        None.
        
        """
        msg_typo['id'] = prep_msg['id']
        msg_typo['threadId'] = prep_msg['threadId']
        msg_typo['to'] = prep_msg['to']
        msg_typo['cc'] = prep_msg['cc']
        msg_typo['bcc'] = prep_msg['bcc']
        msg_typo['from'] = prep_msg['from']
        msg_typo['depth'] = prep_msg['depth']
        msg_typo['date'] = prep_msg['date']
        
        if 'subject' in prep_msg:
            msg_typo['subject'] = prep_msg['subject']
        
        if 'plainEncoding' in prep_msg:
            msg_typo['plainEncoding'] = prep_msg['plainEncoding']
        
    def correct_msgs(self, prep_msg, i):
        """
        Obtains the preprocessed messages and corrects all the typographic errors
        on them. Besides this method saves the preprocessed messages before the 
        correction.
        
        Parameters
        ----------
        prep_msg: dict
            Preprocessed message with the following estructure:
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
                'bodyBase64Plain' : string,
                'bodyBase64Html' : string,   # Optional
                'plainEncoding' : string,    # Optional
                'charLength' : int
            }
        i: int
            It indicates the position of the word from which the typographic 
            correction should be made.
            
        Returns
        -------
        None.
        
        """
        if not('bodyPlain' in prep_msg):
            prep_msg['bodyPlain'] = base64.urlsafe_b64decode(
                        prep_msg['bodyBase64Plain'].encode()).decode()
        # If the body is not an empty string
        if (len(prep_msg['bodyPlain']) > 0):
            msg_typo = {}
            
            msg_typo['bodyPlain'] = prep_msg['bodyPlain']
            self.__get_structured_text(msg_typo)
            if 'corrections' in prep_msg:
                msg_typo['corrections'] = prep_msg['corrections']
            else:
                msg_typo['corrections'] = []
            
            # Sentence index: indicates the initial token of the sentence
            s_ind = -1
            # Sentence init: indicates the position of the first chartacter
            s_ini = 0
            
            no_errors = True
            while (i < len(msg_typo['doc']) and no_errors):
                # If the token stars a sentence
                if msg_typo['doc'][i].is_sent_start:
                    s_ind += 1
                    s_ini = msg_typo['doc'][i].idx
                
                no_errors = self.__is_there_errors(msg_typo['doc'][i])
                
                if no_errors:
                    i += 1
            
            for j in range(len(prep_msg['sentences'])):
                prep_msg['sentences'][j] = [base64.urlsafe_b64encode(
                    t.text.encode()).decode() for t in  
                    prep_msg['sentences'][j]['words']]
            
            self.__copy_data(prep_msg, msg_typo)
            
            msg_typo['charLength'] = len(msg_typo['bodyPlain'])
            msg_typo['bodyBase64Plain'] = base64.urlsafe_b64encode(
                msg_typo['bodyPlain'].encode()).decode()
    
        self.__save_words_oov()