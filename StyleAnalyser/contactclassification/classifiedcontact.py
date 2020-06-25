# -*- coding: utf-8 -*-
"""
Created on Mon May 11 19:11:24 2020

@author: Carlos Moreno Morera
"""

import mongoengine as db

class ClassifiedContact(db.Document):
    """
    Class which manage the MongoDB table about the clasiffied contact.
    
    Attributes
    ----------
    email: db.StringField
        Contact's email address.
    name: db.StringField
        Contact's name.
    category: db.StringField
        Contact's relationship type.
        
    """
    email = db.StringField(required = True, primary_key = True)
    name = db.StringField()
    category = db.StringField()
    
    meta = {
        'db_alias': 'core',
        'collection': 'classifiedcontact'
    }