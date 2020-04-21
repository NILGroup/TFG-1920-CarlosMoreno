# -*- coding: utf-8 -*-
"""
Created on Tue Dec 24 16:28:45 2019

@author: Carlos Moreno Morera
"""
import spacy

NUM_RESOURCE_PER_LIST = 100

NLP = spacy.load('es_core_news_md')

URL_PREP = "http://localhost:5000/preprocessor"