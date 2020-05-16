# -*- coding: utf-8 -*-
"""
Created on Wed May 13 20:11:03 2020

@author: Carlos Moreno Morera
"""
from relationshiptype import RelationshipType

UNUSED_FIELDS = {'threadId', 'sender', 'date', 'subject','metricsSentences', 
                 'wordLength', 'sentLength', 'sentNumWords', 'wordsAppearance'}

K_MAX = len(RelationshipType) + 5