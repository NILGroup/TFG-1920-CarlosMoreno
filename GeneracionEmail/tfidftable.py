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
from math import log

def tf_vector(text, columns, df, ide, corrections = None):
    """
    Calculates the TF vector of the given text.

    Parameters
    ----------
    text : str
        Text from which the TF vector is going to be obtained.
    columns : list
        Columns of the actual TF table.
    df : pd.DataFrame
        Actual TF table.
    ide : str
        Identifier of the given text.
    corrections : list, optional
        List with the typographic corrections of the given text. The default 
        is None.

    Returns
    -------
    tf : dict
        TF vector.

    """
    doc = NLP(text)
    ind_cor = 0
    tf = {}
    
    for c in columns:
        tf[c] = 0
    
    tf['_id'] = ide
    
    for token in doc:
        if token.pos_ != 'SPACE' and token.is_oov and (corrections is not None):
            cor = corrections[ind_cor]
            token = MyToken(**cor)
            ind_cor += 1
            
        if not(token.is_punct or token.like_email or token.like_url or
               token.is_stop):
            word = token.text
            if token.lemma_:
                word = token.lemma_
                
            if word not in tf:
                tf[word] = 0
                df[word] = np.zeros(len(df))
            
            tf[word] += 1
            
    max_f = max(tf.values())
    tf = {k: v/max_f for k, v in tf.items()}
            
    return tf

def generate_TFIDF_table():
    """
    Generates TF-IDF (Term Frequency - Inverse Document Frequency) table of
    the messages.

    Returns
    -------
    tfidf : pd.DataFrame
        TF-IDF table.

    """
    tfidf = pd.DataFrame()
    tfidf['_id'] = []
    
    init_db()
    for msg in CorrectedMessage.objects():
        text = base64.urlsafe_b64decode(msg.bodyBase64Plain.encode()).decode()
        tfidf = tfidf.append(tf_vector(text, tfidf.columns, tfidf, msg.msg_id,
                                       msg.corrections), ignore_index = True)
        
    num_msg = len(tfidf)
    for word in tfidf.drop(columns = '_id').columns:
        idf = log(num_msg / (len(tfidf[tfidf[word] > 0]) + 1))
        tfidf[word] = tfidf[word].apply(lambda tf: tf * idf)
        
    return tfidf