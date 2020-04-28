# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 13:04:10 2020

@author: Carlos
"""

import mongoengine as db

class Metrics(db.Document):
    """
    Class which manage the MongoDB table about the metrics of each message.
    
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
    charLength: db.IntField
        Number of characters of the message's body.
    numStopWords: db.IntField
        Number of stop words of the message's body.
    ADV: db.IntField
        Number of adverbs of the message's body.
    VERB: db.IntField
        Number of verbs of the message's body.
    ADJ: db.IntField
        Number of adjectives of the message's body.
    ADP: db.IntField
        Number of prepositions of the message's body.
    NOUN: db.IntField
        Number of nouns of the message's body.
    PRON: db.IntField
        Number of pronouns of the message's body.
    DET: db.IntField
        Number of determinants of the message's body.
    CONJ: db.IntField
        Number of conjuctions of the message's body.
    numCommas: db.IntField
        Number of commas of the message's body.
    numDots: db.IntField
        Number of dots of the message's body.
    numSemiColon: db.IntField
        Number of semicolons of the message's body.
    num3Dots: db.IntField
        Number of three dots of the message's body.
    numBrackets: db.IntField
        Number of pair of brackets of the message's body.
    numWords: db.IntField
        Number of words of the message's body.
    stopRatio: db.FloatField
        Percentage of stop words of the message's body.
    difficultyLevel: db.FloatField
        Level of difficulty of the message's body.
    richnessVocab: db.FloatField
        Richness of the vocabulary of the message's body.
    richnessYule: db.FloatField
        Yule's richness of vocabulary index of the message's body.
    meanSentLen: db.FloatField
        Average word count per sentence of the message's body.
    meanWordLen: db.FloatField
        Mean word length of the message's body.
    numDifWords: db.IntField
        Number of different words of the message's body.
    SimpsonIndex: db.FloatField
        Simpson's Index of the message's body.
    entropy: db.FloatField
        Entropy of the message's body.
    verbAdjectiveRatio: db.FloatField
        Relation between number of verbs and number of adjectives of the
        message's body.
    detPronRatio: db.FloatField
        Relation between number of determinants and number of pronouns of the
        message's body.
    wordLength: db.DictField
        Dictionary which stores the number of words of each length that appears
        in the message's body.
    sentLength: db.DictField
        Dictionary which stores the number of sentences of each length (number
        of characters) that appears in the message's body.
    sentNumWords: db.DictField
        Dictionary which stores the number of sentences of each length (number
        of words) that appears in the message's body.
    metricsSentences: db.ListField
        List that stores the metrics of each sentence of the message's body.
    wordsAppearance: db.DictField
        Dictionary which stores the number of appearances of each word of the
        message's body.
    
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
    charLength = db.IntField()
    numStopWords = db.IntField()
    ADV = db.IntField()
    VERB = db.IntField()
    ADJ = db.IntField()
    ADP = db.IntField()
    NOUN = db.IntField()
    PRON = db.IntField()
    DET = db.IntField()
    CONJ = db.IntField()
    numCommas = db.IntField()
    numDots = db.IntField()
    numSemiColon = db.IntField()
    num3Dots = db.IntField()
    numBrackets = db.IntField()
    numWords = db.IntField()
    stopRatio = db.FloatField()
    difficultyLevel = db.FloatField()
    richnessVocab = db.FloatField()
    richnessYule = db.FloatField()
    meanSentLen = db.FloatField()
    meanWordLen = db.FloatField()
    numDifWords = db.IntField()
    SimpsonIndex = db.FloatField()
    entropy = db.FloatField()
    verbAdjectiveRatio = db.FloatField()
    detPronRatio = db.FloatField()
    wordLength = db.DictField()
    sentLength = db.DictField()
    sentNumWords = db.DictField()
    metricsSentences = db.ListField()
    wordsAppearance = db.DictField()
    
    meta = {
        'db_alias': 'core',
        'collection': 'metrics'
    }