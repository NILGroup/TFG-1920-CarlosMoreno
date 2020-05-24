# -*- coding: utf-8 -*-
"""
Created on Sat Jan 25 17:40:38 2020

@author: Carlos Moreno Morera
"""

class MyToken:
    """
    Class MyToken replaces the Spacy's Token class for those token which are
    out of vocabulary.
    
    Attributes
    ----------
    text: str
        Verbatim text content.
    is_punct: bool
        Is the token punctuation?
    is_right_punct: bool
        Is the token a right punctuation mark?
    is_left_punct: bool
        Is the token a left punctuation mark?
    like_url: bool
        Does the token resemble a URL?
    like_email: bool
        Does the token resemble an email address?
    lemma_: str
        Base form of the token, with no inflectional suffixes.
    is_stop: bool
        Is the token a stop word?
    pos_: str
        Part of speech.
    is_bracket: bool
        Is the token a bracket?
        
    """
                        
    def __init__(self, **kwargs):
        self.text = kwargs['text']
        self.is_punct = kwargs['is_punct']
        self.lemma_ = ''
        self.pos_ = ''
        self.is_right_punct = False
        self.is_left_punct = False
        self.is_bracket = False
        
        if self.is_punct:
            self.is_right_punct = kwargs['is_right_punct']
            self.is_left_punct = kwargs['is_left_punct']
            self.is_bracket = kwargs['is_bracket']
        
        self.like_url = kwargs['like_url']
        self.like_email = kwargs['like_email']
        
        if 'lemma_' in kwargs:
            self.lemma_ = kwargs['lemma_']
            
        self.is_stop = kwargs['is_stop']
        
        if 'pos_' in kwargs:
            self.pos_ = kwargs['pos_']
        