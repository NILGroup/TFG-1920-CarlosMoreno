# -*- coding: utf-8 -*-
"""
Created on Sun Jan 26 11:20:48 2020

@author: Carlos Moreno Morera
"""
import mongoengine

class MyToken(mongoengine.Document):
    """
    MyToken class manage mongoDB table which stores Spacy's Tokens which are
    out of vocabulary and they are right.
    
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
    
    text = mongoengine.StringField(required=True, primary_key = True)
    is_punct = mongoengine.BooleanField(default = False)
    is_right_punct = mongoengine.BooleanField(default = False)
    is_left_punct = mongoengine.BooleanField(default = False)
    like_url = mongoengine.BooleanField(default = False)
    like_email = mongoengine.BooleanField(default = False)
    lemma_ = mongoengine.StringField()
    is_stop = mongoengine.BooleanField(default = False)
    pos_ = mongoengine.StringField()
    is_bracket = mongoengine.BooleanField(default = False)
    
    meta = {
        'db_alias': 'core',
        'collection': 'mytoken'
    }