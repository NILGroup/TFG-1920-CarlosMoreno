# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 19:03:23 2020

@author: Carlos
"""

import mongoengine as db
from typocorrection.correction import Correction

class CorrectedMessage(db.Document):
    """
    Class which manage the MongoDB table about the corrected messages.
    
    Attributes
    ----------
    msg_id: db.StringField
        Message's identifier. It must be unique because we will identify each
        message by using it.
    threadId: db.StringField
        Identifier of the message's thread.
    to: db.ListField
        List of direct message's recipients.
    cc: db.ListField
        List of message's recipients who recieved the message as a copy of the
        information sent to the recipients in 'to' attributte.
    bcc: db.ListField
        List of message's recipients who recieved the message as a copy of the
        information sent to the recipients in 'to' attributte. Each bcc 
        addressee is hidden from the rest of recipients.
    sender: db.StringField
        Message's sender.
    depth: db.IntField
        Number of messages which precede it.
    date: db.LongField
        Epoch ms.
    subject: db.StringField
        Message's subject.
    bodyBase64Plain: db.StringField
        Message's body as a Base64 encoded plain text.
    plainEncoding: db.StringField
        Original message's encoding.
    charLength: db.IntField
        Number of characters of the message's body.
    corrections: db.EmbeddedDocumentListField
        Information about the words that the Spacy's model considers out of
        vocabulary and they are not typographic errors.
        
    """
    msg_id = db.StringField(required=True, primary_key = True)
    threadId = db.StringField(required = True)
    to = db.ListField()
    cc = db.ListField()
    bcc = db.ListField()
    sender = db.StringField(required = True)
    depth = db.IntField(required = True)
    date = db.LongField(required = True)
    subject = db.StringField()
    bodyBase64Plain = db.StringField()
    plainEncoding = db.StringField()
    charLength = db.IntField()
    corrections = db.EmbeddedDocumentListField(Correction, default = [])
    
    meta = {
        'db_alias': 'core',
        'collection': 'correctedmessage'
    }