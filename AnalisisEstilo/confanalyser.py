# -*- coding: utf-8 -*-
"""
Created on Tue Dec 24 16:28:45 2019

@author: Carlos Moreno Morera
"""

import spacy

NUM_RESOURCE_PER_LIST = 100

NLP = spacy.load('es_core_news_md')

URL_PREP = "http://localhost:5000/preprocessor"
URL_TYPO_CORRECT = "http://localhost:4000/typocorrector/correct"
URL_TYPO_SAVE = "http://localhost:4000/typocorrector/saveoov"

IS_LPUNCT = 'Is it left punctuation?'
IS_RPUNCT = 'Is it right punctuation?'
IS_BRACKET= 'Is the token a bracket?'
TOK_LEM = "Introduce the token's lemma: "
TOK_POS = "Introduce the token's pos: "
DISC_MSG = 'Do you want to discard it?'

SAVE_OOV = 'Do you want to save this information in order to know what to do in the future?'