# -*- coding: utf-8 -*-
"""
Created on Sun Apr 26 14:59:28 2020

@author: Carlos
"""

import mongoengine

class Correction(mongoengine.EmbeddedDocument):
    """
    Correction class substitutes Spacy's Tokens when the word is out of vocabulary.
    
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
    position: int
        Index which indicates the position of the token.
        
    """
    
    text = mongoengine.StringField(required = True)
    is_punct = mongoengine.BooleanField(default = False)
    is_right_punct = mongoengine.BooleanField(default = False)
    is_left_punct = mongoengine.BooleanField(default = False)
    like_url = mongoengine.BooleanField(default = False)
    like_email = mongoengine.BooleanField(default = False)
    lemma_ = mongoengine.StringField()
    is_stop = mongoengine.BooleanField(default = False)
    pos_ = mongoengine.StringField()
    is_bracket = mongoengine.BooleanField(default = False)
    
    position = mongoengine.IntField()