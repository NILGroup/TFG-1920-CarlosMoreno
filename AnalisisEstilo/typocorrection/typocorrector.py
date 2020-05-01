# -*- coding: utf-8 -*-
"""
Created on Fri Dec 20 22:09:13 2019

@author: Carlos Moreno Morera
"""

from __future__ import print_function
import base64
from correction import Correction
from correctedmessage import CorrectedMessage
from typocode import TypoCode

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
                (Correction.objects(text = tok.text).first() is None))
    
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
                    'sender' : string,
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
        msg_typo['sender'] = prep_msg['sender']
        msg_typo['depth'] = prep_msg['depth']
        msg_typo['date'] = prep_msg['date']
        
        if 'subject' in prep_msg:
            msg_typo['subject'] = prep_msg['subject']
        
        if 'plainEncoding' in prep_msg:
            msg_typo['plainEncoding'] = prep_msg['plainEncoding']
            
    def __save_cor_msg(self, typo):
        """
        Save in the database the corrected message.

        Parameters
        ----------
        typo : dict
            Corrected message with the following estructure:
            {
                'id' : string,
                'threadId' : string,
                'to' : [ string ],
                'cc' : [ string ],
                'bcc' : [ string ],
                'sender' : string,
                'depth' : int,               # How many messages precede it
                'date' : long,               # Epoch ms
                'subject' : string,          # Optional
                'bodyPlain' : string,
                'bodyBase64Plain' : string,
                'plainEncoding' : string,    # Optional
                'charLength' : int
                'doc' : Spacy's Doc
                'corrections' : [
                    {
                        'text': str,
                        'is_punct': bool,
                        'is_right_punct': bool,
                        'is_left_punct': bool,
                        'like_url': bool,
                        'like_email': bool,
                        'lemma_': str,
                        'is_stop': bool,
                        'pos_': str,
                        'is_bracket': bool,
                        'position': int
                    }
                ]
            }

        Returns
        -------
        None.

        """        
        msg = CorrectedMessage()
        msg.msg_id = typo['id']
        msg.threadId = typo['threadId']
        for recipient in typo['to']:
            msg.to.append(recipient)
        for recipient in typo['cc']:
            msg.cc.append(recipient)
        for recipient in typo['bcc']:
            msg.bcc.append(recipient)
        msg.sender = typo['sender']
        msg.date = typo['date']
        
        if 'subject' in typo:
            msg.subject = typo['subject']
            
        msg.depth = typo['depth']
        msg.bodyBase64Plain = typo['bodyBase64Plain']
        
        if 'plainEncoding' in typo:
            msg.plainEncoding = typo['plainEncoding']
        
        msg.corrections = []
        for c in typo['corrections']:
            msg.corrections.append(c)

        msg.charLength = typo['charLength']
        msg.save()
        
    def correct_msg(self, prep_msg, i):
        """
        Obtains the preprocessed message and corrects all the typographic errors
        on it. Besides this method saves the preprocessed messages before the 
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
                'sender' : string,
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
        dict: Result of the proces. It has the following structure:
            {
                'typoCode': <enum 'TypoCode'>,
                'index': int,
                'typoError': str,
                'token_idx': int,
                'message': {
                    'id' : string,
                    'threadId' : string,
                    'to' : [ string ],
                    'cc' : [ string ],
                    'bcc' : [ string ],
                    'sender' : string,
                    'depth' : int,               # How many messages precede it
                    'date' : long,               # Epoch ms
                    'subject' : string,          # Optional
                    'bodyPlain' : string,
                    'bodyBase64Plain' : string,
                    'plainEncoding' : string,    # Optional
                    'charLength' : int,
                    'corrections' : [
                        {
                            'text': str,
                            'is_punct': bool,
                            'is_right_punct': bool,
                            'is_left_punct': bool,
                            'like_url': bool,
                            'like_email': bool,
                            'lemma_': str,
                            'is_stop': bool,
                            'pos_': str,
                            'is_bracket': bool,
                            'position': int
                        }
                    ]
                }
            }
        
        """
        response = TypoCode.notAnalysed
        word = None
        tok_idx = None
        
        if (not('bodyPlain' in prep_msg) and 
            not(CorrectedMessage.objects(msg_id = prep_msg['id']).first())):
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
                no_errors = not(self.__is_there_errors(msg_typo['doc'][i]))
                
                if no_errors:
                    i += 1
            
            self.__copy_data(prep_msg, msg_typo)
            
            msg_typo['charLength'] = len(msg_typo['bodyPlain'])
            msg_typo['bodyBase64Plain'] = base64.urlsafe_b64encode(
                msg_typo['bodyPlain'].encode()).decode()
            
            if no_errors:
                self.__save_cor_msg(msg_typo)
                response = TypoCode.successful
            else:
                response = TypoCode.typoFound
                word = msg_typo['doc'][i].text
                tok_idx = msg_typo['doc'][i].idx
                
            del msg_typo['doc']
                
        return {'typoCode' : response.name, 'index' : i, 'typoError': word, 
                'token_idx' : tok_idx, 'message' : msg_typo}
    
    def save_oov(self, cor):
        """
        Saves the given token in the mongoDB.

        Parameters
        ----------
        cor : dict
            Correction which we are going to save. It has the following structure:
                {
                    'text': str,
                    'is_punct': bool,
                    'is_right_punct': bool,
                    'is_left_punct': bool,
                    'like_url': bool,
                    'like_email': bool,
                    'lemma_': str,
                    'is_stop': bool,
                    'pos_': str,
                    'is_bracket': bool
                }

        Returns
        -------
        None.

        """
        c = Correction(**cor)
        c.save()