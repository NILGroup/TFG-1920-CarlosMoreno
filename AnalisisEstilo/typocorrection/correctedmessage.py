# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 19:03:23 2020

@author: Carlos
"""

import mongoengine
from correction import Correction

class CorrectedMessage(mongoengine.Document):
    """
    Class which manage the MongoDB table about the corrected messages.
    
    Attributes
    ----------
    msg_id: mongoengine.StringField
        Message's identifier. It must be unique because we will identify each
        message by using it.
    threadId: mongoengine.StringField
        Identifier of the message's thread.
    to: mongoengine.ListField
        List of direct message's recipients.
    cc: mongoengine.ListField
        List of message's recipients who recieved the message as a copy of the
        information sent to the recipients in 'to' attributte.
    bcc: mongoengine.ListField
        List of message's recipients who recieved the message as a copy of the
        information sent to the recipients in 'to' attributte. Each bcc 
        addressee is hidden from the rest of recipients.
    sender: mongoengine.StringField
        Message's sender.
    depth: mongoengine.IntField
        Number of messages which precede it.
    date: mongoengine.LongField
        Epoch ms.
    subject: mongoengine.StringField
        Message's subject.
    bodyBase64Plain: mongoengine.StringField
        Message's body as a Base64 encoded plain text.
    plainEncoding: mongoengine.StringField
        Original message's encoding.
    charLength: mongoengine.IntField
        Number of characters of the message's body.
    corrections: mongoengine.EmbeddedDocumentListField
        Information about the words that the Spacy's model considers out of
        vocabulary and they are not typographic errors.
    """
    msg_id = mongoengine.StringField(required=True, primary_key = True)
    threadId = mongoengine.StringField(required = True)
    to = mongoengine.ListField()
    cc = mongoengine.ListField()
    bcc = mongoengine.ListField()
    sender = mongoengine.StringField(required = True)
    depth = mongoengine.IntField(required = True)
    date = mongoengine.LongField(required = True)
    subject = mongoengine.StringField()
    bodyBase64Plain = mongoengine.StringField()
    plainEncoding = mongoengine.StringField()
    charLength = mongoengine.IntField()
    corrections = mongoengine.EmbeddedDocumentListField(Correction)
    
    meta = {
        'db_alias': 'core',
        'collection': 'correctedmessage'
    }