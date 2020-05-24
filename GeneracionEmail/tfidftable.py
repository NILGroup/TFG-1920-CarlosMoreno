# -*- coding: utf-8 -*-
"""
Created on Sat May 23 20:13:54 2020

@author: Carlos Moreno Morera
"""

from initdb import init_db
from correctedmessage import CorrectedMessage
import pandas as pd
import base64
from conftfid import NLP
import numpy as np
from mytoken import MyToken

def tf_vector(text, columns, df = None, msg = None):
    doc = NLP(text)
    ind_cor = 0
    tf = {}
    
    for c in columns:
        tf[c] = 0
    
    if msg is not None:
        tf['_id'] = msg.msg_id
    
    for token in doc:
        if token.pos_ != 'SPACE' and token.is_oov and (msg is not None):
            cor = msg.corrections[ind_cor]
            token = MyToken(**cor)
            ind_cor += 1
            
        if not(token.is_punct or token.like_email or token.like_url or
               token.is_stop):
            word = token.text
            if token.lemma_:
                word = token.lemma_
                
            if word not in tf:
                tf[word] = 0
                if df is not None:
                    df[word] = np.zeros(len(df))
            
            tf[word] += 1
            
    max_f = max(tf.values())
    tf = {k: v/max_f for k, v in tf.items()}
            
    return tf

def generate_TFIDF_table():
    tfidf = pd.DataFrame()
    tfidf['_id'] = []
    
    init_db()
    for msg in CorrectedMessage.objects():
        text = base64.urlsafe_b64decode(msg.bodyBase64Plain.encode()).decode()
        tfidf = tfidf.append(tf_vector(text, tfidf.columns, tfidf, msg), 
                             ignore_index = True)