# -*- coding: utf-8 -*-
"""
Created on Sun May 24 20:52:14 2020

@author: Carlos Moreno Morera
"""

import os.path
from tfidftable import generate_TFIDF_table, tf_vector
from conflsi import TF_IDF_FILE, NUM_DIM
import pandas as pd
from sklearn.decomposition import TruncatedSVD
from math import log, sqrt
import numpy as np

def get_TFIDF_table():
    """
    Obtains the TF-IDF table. If it is not saved as a .csv file, it will
    be created.

    Returns
    -------
    pd.DataFrame
        TF-IDF table.

    """
    if os.path.isfile(TF_IDF_FILE):
        return pd.read_csv(TF_IDF_FILE)
    else:
        tfidf = generate_TFIDF_table()
        tfidf.to_csv(TF_IDF_FILE, index = False)
        return tfidf
    
def truncate_SVD(tfidf, tfidf_query):
    """
    Truncates the Singular Value Descomposition of the given DataFrame.

    Parameters
    ----------
    tfidf : pd.DataFrame
        DataFrame which represents the TF-IDF table.
    tfidf_query : dict
        Dictionary which represents the TF-IDF vector of the query.

    Returns
    -------
    pd.DataFrame
        Truncated SVD DataFrame.

    """
    # All the columns except the column id
    if (len(tfidf.columns) - 1) > NUM_DIM:
        trun_svd = TruncatedSVD(n_components = NUM_DIM, algorithm = 'arpack')
        trun_tfidf = trun_svd.fit_transform(tfidf.drop(columns = '_id'))

        trun_query = np.zeros(shape = (1, NUM_DIM))
        for i in range(NUM_DIM):
            j = 0
            for word in tfidf.drop(columns = '_id').columns:
                trun_query[0][i] += tfidf_query[word] * trun_svd.components_[i][j]
                j += 1
                
        trun_tfidf = pd.DataFrame(trun_tfidf)
        trun_tfidf['_id'] = tfidf['_id']
        trun_query = pd.DataFrame(trun_query)
        trun_query['_id'] = 'query'
        return trun_tfidf.append(trun_query, ignore_index = True)
    else:
        tfidf_query['_id'] = 'query'
        return tfidf.append(tfidf_query, ignore_index = True)
    
def dot_product(u, v):
    """
    Calculates the dot product of the given vectors.

    Parameters
    ----------
    u : Series
        First given vector.
    v : Series
        Second given vector.

    Returns
    -------
    dot_prod : float
        Dot product of the given vectors.

    """
    dot_prod = 0
    for i in range(len(u)):
        dot_prod += u[i] * v[i]
    return dot_prod
    
def norm(v):
    """
    Calculates the norm of the given vector

    Parameters
    ----------
    v : Series
        Given vector.

    Returns
    -------
    float
        Norm of the given vector.

    """
    return sqrt(dot_product(v, v))

def latent_semantic_indexing(query):
    """
    Obtains the LSI (Latent Semantic Indexing) result of the given query.

    Parameters
    ----------
    query : str
        Query with keywords.

    Returns
    -------
    similar_docs : list
        List of the identifiers of the documents which are result of the LSI.

    """
    tfidf = get_TFIDF_table()
        
    tf_query = tf_vector(query, tfidf.columns, tfidf, 'query')
    
    tfidf_query = {}
    num_doc = len(tfidf)
    for word in tfidf.drop(columns = '_id').columns:
        idf = log(num_doc / (len(tfidf[tfidf[word] > 0]) + 1))
        tfidf_query[word] = tf_query[word] * idf
    
    trun_tfidf = truncate_SVD(tfidf, tfidf_query)
    trun_tfidf.set_index('_id', inplace = True)
    
    q = trun_tfidf.loc['query']
    norm_q = norm(q)
    max_sim = -2
    similar_docs = []
    
    for index, row in trun_tfidf.iterrows():
        if row['_id'] != 'query':
            sim = dot_product(q, row.drop('_id'))/(norm_q * norm(row.drop('_id')))
            
            if sim >= max_sim:
                if sim > max_sim:
                    similar_docs.clear()
                    max_sim = sim
                similar_docs.append(row['_id'])
                
    return similar_docs
                