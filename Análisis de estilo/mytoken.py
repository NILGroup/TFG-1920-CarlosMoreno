# -*- coding: utf-8 -*-
"""
Created on Sun Jan 26 11:20:48 2020

@author: Carlos Moreno Morera
"""
import mongoengine

class MyToken(mongoengine.EmbeddedDocument):
    """
    MyToken class substitutes Spacy's Tokens when the word is out of vocabulary.
    
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
    sentenceIndex: int
        Index of the sentence where the typographic error is.
    sentenceInit: int
        Index of the begining of the sentence in the complete text.
        
    """
    
    text = mongoengine.StringField()
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
    sentenceIndex = mongoengine.IntField()
    sentenceInit = mongoengine.IntField()
    
    def __init__(self, text = '', is_punct = False, is_right_punct = False,
                 is_left_punct = False, like_url = False, like_email = False,
                 lemma_ = '', is_stop = False, pos_ = '', is_bracket = False):
        """
        Constructor of MyToken class.
        
        Parameters
        ----------
        text: str (optional)
            Verbatim text content.
        is_punct: bool (optional)
            Is the token punctuation?
        is_right_punct: bool (optional)
            Is the token a right punctuation mark?
        is_left_punct: bool (optional)
            Is the token a left punctuation mark?
        like_url: bool (optional)
            Does the token resemble a URL?
        like_email: bool (optional)
            Does the token resemble an email address?
        lemma_: str (optional)
            Base form of the token, with no inflectional suffixes.
        is_stop: bool (optional)
            Is the token a stop word?
        pos_: str (optional)
            Part of speech.
        is_bracket: bool (optional)
            Is the token a bracket?
        
        Returns
        -------
        Constructed MyToken class.
        
        """
        self.text = text
        self.is_punct = is_punct
        self.is_right_punct = is_right_punct
        self.is_left_punct = is_left_punct
        self.like_url = like_url
        self.like_email = like_email
        self.lemma_ = lemma_
        self.is_stop = is_stop
        self.pos_ = pos_
        self.is_bracket = is_bracket