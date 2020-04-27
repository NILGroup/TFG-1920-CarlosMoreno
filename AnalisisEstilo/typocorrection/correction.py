# -*- coding: utf-8 -*-
"""
Created on Sun Apr 26 14:59:28 2020

@author: Carlos
"""

import mongoengine as db

class Correction(db.EmbeddedDocument):
    """
    Correction class substitutes Spacy's Tokens when the word is out of vocabulary.
    
    Attributes
    ----------
    text: db.StringField
        Verbatim text content.
    is_punct: db.BooleanField
        Is the token punctuation?
    is_right_punct: db.BooleanField
        Is the token a right punctuation mark?
    is_left_punct: db.BooleanField
        Is the token a left punctuation mark?
    like_url: db.BooleanField
        Does the token resemble a URL?
    like_email: db.BooleanField
        Does the token resemble an email address?
    lemma_: db.StringField
        Base form of the token, with no inflectional suffixes.
    is_stop: db.BooleanField
        Is the token a stop word?
    pos_: db.StringField
        Part of speech.
    is_bracket: db.BooleanField
        Is the token a bracket?
    position: db.IntField
        Index which indicates the position of the token.
        
    """
    
    text = db.StringField(required = True)
    is_punct = db.BooleanField(default = False)
    is_right_punct = db.BooleanField(default = False)
    is_left_punct = db.BooleanField(default = False)
    like_url = db.BooleanField(default = False)
    like_email = db.BooleanField(default = False)
    lemma_ = db.StringField()
    is_stop = db.BooleanField(default = False)
    pos_ = db.StringField()
    is_bracket = db.BooleanField(default = False)
    
    position = db.IntField()