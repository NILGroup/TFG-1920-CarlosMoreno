# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 17:45:20 2020

@author: Carlos
"""

import mongoengine as db

class PreprocessedMessage(db.Document):
    """
    Class which manage the MongoDB table about the preprocessed messages.
    
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
    bodyBase64Html: db.StringField
        Message's body as a Base64 encoded html text.
    plainEncoding: db.StringField
        Original message's encoding.
    charLength: db.IntField
        Number of characters of the message's body.
    
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
    bodyBase64Plain = db.StringField(required = True)
    bodyBase64Html = db.StringField()
    plainEncoding = db.StringField()
    charLength = db.IntField()
    
    meta = {
        'db_alias': 'core',
        'collection': 'preprocessedmessage'
    }