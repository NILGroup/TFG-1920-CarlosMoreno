# -*- coding: utf-8 -*-
"""
Created on Sat Jan 25 17:40:38 2020

@author: Carlos Moreno Morera
"""

CSV_TYPO_COL = ['id', 'threadId', 'to', 'cc', 'bcc', 'from', 'depth', 'date', 'subject', 
               'bodyBase64Plain', 'plainEncoding', 'charLength', 'sentences',
               'corrections']

CSV_MET_COL = ['id', 'threadId', 'to', 'cc', 'bcc', 'from', 'depth', 'date', 'subject', 
               'numStopWords', 'ADV', 'VERB', 'ADJ', 'ADP', 'NOUN', 'PRON', 'DET', 'CONJ',
               'numCommas', 'numDots', 'numSemiColon', 'num3Dots', 'numBrackets',
               'wordLength', 'charLength', 'numWords', 'sentLength', 'sentNumWords',
               'metricsSentences', 'stopRatio', 'difficultyLevel', 'richnessVocab',
               'wordsAppearance', 'richnessYule', 'meanSentLen', 'meanWordLen',
               'numDifWords', 'verbAdjectiveRatio', 'detPronRatio', 'SimpsonIndex',
               'entropy']

POS = {'ADV', 'VERB', 'ADJ', 'ADP', 'NOUN', 'PRON', 'DET', 'CONJ'}