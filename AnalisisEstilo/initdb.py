# -*- coding: utf-8 -*-
"""
Created on Wed Apr 22 17:50:25 2020

@author: Carlos
"""

import mongoengine

def init_db():
    """
    Inits the connection with the MongoDB.

    Returns
    -------
    None.

    """
    mongoengine.register_connection(alias='core', name='analysis')