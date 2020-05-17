# -*- coding: utf-8 -*-
"""
Created on Wed May 13 20:11:03 2020

@author: Carlos Moreno Morera
"""
from contactclassification.relationshiptype import RelationshipType

UNUSED_FIELDS = {'threadId', 'sender', 'date', 'subject','metricsSentences', 
                 'wordLength', 'sentLength', 'sentNumWords', 'wordsAppearance'}

K_MAX = len(RelationshipType) + 5
MAX_ITER = 100

COLORS = ['blue', 'red', 'green','purple', 'yellow', 'black', 'brown', 'orange',
          'lime', 'pink', 'magenta', 'cyan']