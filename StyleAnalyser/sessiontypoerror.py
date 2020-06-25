# -*- coding: utf-8 -*-
"""
Created on Tue May  5 22:29:42 2020

@author: Carlos Moreno Morera
"""

import mongoengine as db

class SessionTypoError(db.Document):
    """
    SessionTypoError class manage mongoDB table which stores the correction of
    typographic errors in a session.
    
    Attributes
    ----------
    text: db.StringField
        Text of the error.
    typo_error: db.BooleanField
        Indicates if it is a real typographic error or a out of vocabulary token.
    solution: db.DictField
        Dictionary which stores how to solve this error.
        
    """
    text = db.StringField(required=True, primary_key = True)
    typo_error = db.BooleanField(default = False)
    solution = db.DictField()
    
    meta = {
        'db_alias': 'core',
        'collection': 'sessiontypoerror'
    }
    