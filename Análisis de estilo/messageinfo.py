# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 17:45:20 2020

@author: Carlos
"""

import mongoengine

class MessageInfo(mongoengine.Document):
    """
    
    {
            'id' : string,
            'threadId' : string,
            'to' : [ string ],
            'cc' : [ string ],
            'bcc' : [ string ],
            'from' : string,
            'depth' : int,               # How many messages precede it
            'date' : long,               # Epoch ms
            'subject' : string,
            'bodyPlain' : string,
            'bodyHtml' : string,
            'bodyBase64Plain' : string,
            'bodyBase64Html' : string,
            'plainEncoding' : string,
            'charLength' : int
        }
    
    """
    msg_id = mongoengine.StringField(required=True, primary_key = True)
    thread_id = mongoengine.StringField(required = True)
    to = mongoengine.ListField()
    cc = mongoengine.ListField()
    bcc = mongoengine.ListField()
    sender = mongoengine.StringField(required = True)
    depth = mongoengine.IntField(required = True)
    date = mongoengine.LongField(required = True)
    subject = mongoengine.StringField()
    bodyBase64Plain = mongoengine.StringField()
    bodyBase64Html = mongoengine.StringField()
    plainEncoding = mongoengine.StringField()
    charLength = mongoengine.IntField()