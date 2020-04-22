# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 19:03:23 2020

@author: Carlos
"""

import mongoengine
from mytoken import MyToken

class CorrectedMessage(mongoengine.Document):
    msg_id = mongoengine.StringField(required=True, primary_key = True)
    thread_id = mongoengine.StringField(required = True)
    to = mongoengine.ListField()
    cc = mongoengine.ListField()
    bcc = mongoengine.ListField()
    sender = mongoengine.StringField(required = True)
    depth = mongoengine.IntField(required = True)
    date = mongoengine.LongField(required = True)
    subject = mongoengine.StringField()
    bodyPlain = mongoengine.StringField()
    bodyBase64Plain = mongoengine.StringField()
    plainEncoding = mongoengine.StringField()
    charLength = mongoengine.IntField()
    corrections = mongoengine.EmbeddedDocumentListField(MyToken)