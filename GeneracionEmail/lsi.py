# -*- coding: utf-8 -*-
"""
Created on Sun May 24 20:52:14 2020

@author: Carlos Moreno Morera
"""

import os.path
from tfidftable import generate_TFIDF_table, tf_vector
from conflsi import TF_IDF_FILE, NUM_DIM, TRUNC_TF_IDF_FILE, TRUNC_SVD_FILE
import pandas as pd
from sklearn.decomposition import TruncatedSVD
from math import log, sqrt
import numpy as np
import pickle

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
        print('Loading TF-IDF table...')
        return pd.read_csv(TF_IDF_FILE)
    else:
        print('Generating TF-IDF table...')
        tfidf = generate_TFIDF_table()
        print('Saving TF-IDF table in ' + TF_IDF_FILE + '...')
        tfidf.to_csv(TF_IDF_FILE, index = False)
        return tfidf
    
def get_truncated_tfidf_and_truncated_svd(tfidf):
    trun_tfidf = None
    trun_svd = None
    
    if os.path.isfile(TRUNC_TF_IDF_FILE) and os.path.isfile(TRUNC_SVD_FILE):
        print('Loading truncated TF-IDF table...')
        trun_tfidf = pd.read_csv(TRUNC_TF_IDF_FILE)
        print(f'Shape of truncated TF-IDF table: {trun_tfidf.shape}.')
        print('Loading components of truncated SVD...')
        with open(TRUNC_SVD_FILE, 'r') as f:
            trun_svd = pickle.load(f)
    else:
        print('Generating components of truncated SVD...')
        trun_svd = TruncatedSVD(n_components = NUM_DIM, algorithm = 'arpack')
        print('Generating truncated TF-IDF table...')
        trun_tfidf = trun_svd.fit_transform(tfidf.drop(columns = '_id'))
        
        print('Saving components of truncated SVD in ' + TRUNC_SVD_FILE + '...')
        with open(TRUNC_SVD_FILE, 'wb') as pickle_file:
            pickle.dump(trun_svd, pickle_file)
        
        trun_tfidf = pd.DataFrame(trun_tfidf)
        trun_tfidf['_id'] = tfidf['_id']
        print(f'Shape of truncated TF-IDF table: {trun_tfidf.shape}.')
        print('Saving truncated TF-IDF table in ' + TRUNC_TF_IDF_FILE + '...')
        trun_tfidf.to_csv(TRUNC_TF_IDF_FILE, index = False)
        
    return trun_tfidf, trun_svd
    
    
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
    if (len(tfidf.columns) - 1) <= NUM_DIM:
        tfidf_query['_id'] = 'query'
        return tfidf.append(tfidf_query, ignore_index = True)
    
    trun_tfidf, trun_svd = get_truncated_tfidf_and_truncated_svd(tfidf)

    trun_query = np.zeros(shape = (1, NUM_DIM))
    for i in range(NUM_DIM):
        j = 0
        for word in tfidf.drop(columns = '_id').columns:
            trun_query[0][i] += tfidf_query[word] * trun_svd.components_[i][j]
            j += 1
            
    trun_query = pd.DataFrame(trun_query)
    trun_query['_id'] = 'query'
    print('Truncated query:')
    print(trun_query)
    return trun_tfidf.append(trun_query, ignore_index = True)
    
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
    print(f'Shape of the TF-IDF table: {tfidf.shape}.')
        
    print("Calculating query's TF-IDF vector...")
    tf_query = tf_vector(query, tfidf.columns, tfidf, 'query')
    
    tfidf_query = {}
    num_doc = len(tfidf)
    for word in tfidf.drop(columns = '_id').columns:
        idf = log(num_doc / (len(tfidf[tfidf[word] > 0]) + 1))
        tfidf_query[word] = tf_query[word] * idf
    
    print("Query's TF-IDF vector:")
    print(pd.DataFrame([tfidf_query.values()], columns = tfidf_query.keys()))
    
    trun_tfidf = truncate_SVD(tfidf, tfidf_query)
    trun_tfidf.set_index('_id', inplace = True)
    
    print('Looking for the document most similar to the query...')
    q = trun_tfidf.loc['query']
    trun_tfidf.drop('query', inplace = True)
    norm_q = norm(q)
    # The minimum value of similarity is -1
    max_sim = -2
    similar_docs = []
    
    for index, row in trun_tfidf.iterrows():
        sim = dot_product(q, row.drop('_id'))/(norm_q * norm(row.drop('_id')))
        
        if sim >= max_sim:
            if sim > max_sim:
                similar_docs.clear()
                max_sim = sim
            similar_docs.append(row['_id'])
                
    return similar_docs
                