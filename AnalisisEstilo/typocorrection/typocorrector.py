# -*- coding: utf-8 -*-
"""
Created on Fri Dec 20 22:09:13 2019

@author: Carlos Moreno Morera
"""

from __future__ import print_function
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
        self.nlp = nlp
                                    
    def __is_there_errors(self, tok):
        """
        Given a token checks if it is out of the vocabulary of our model.

        Parameters
        ----------
        tok : spacy.Token
            Token which we have to check if it is out of vocabulary.

        Returns
        -------
        bool: False if it is a token in the vocabulary of our model and True
        otherwise.

        """
        return (tok.pos_ != 'SPACE' and tok.is_oov and 
                (MyToken.objects(text = tok.text).first() is None))
    
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
            msg_typo['doc'] = self.nlp(msg_typo['bodyPlain'])
            if 'corrections' in prep_msg:
                msg_typo['corrections'] = prep_msg['corrections']
            else:
                msg_typo['corrections'] = []
            
            no_errors = True
            while (i < len(msg_typo['doc']) and no_errors):
                no_errors = self.__is_there_errors(msg_typo['doc'][i])
                
                if no_errors:
                    i += 1
            
            self.__copy_data(prep_msg, msg_typo)
            
            msg_typo['charLength'] = len(msg_typo['bodyPlain'])
            msg_typo['bodyBase64Plain'] = base64.urlsafe_b64encode(
                msg_typo['bodyPlain'].encode()).decode()