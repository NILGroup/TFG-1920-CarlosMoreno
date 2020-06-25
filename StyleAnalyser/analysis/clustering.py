# -*- coding: utf-8 -*-
"""
Created on Thu May 21 14:34:52 2020

@author: Carlos Moreno Morera
"""

import os, sys
initial_dir = os.getcwd()
os.chdir('../')
if not(os.getcwd() in sys.path):
    sys.path.append(os.getcwd())
    
import numpy as np
from sklearn.cluster import KMeans
from sklearn.cluster import DBSCAN
from analysis.confanalysis import K_MAX, MAX_ITER
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
import pandas as pd
from analysis.treeanalysis import replace_nan
from sklearn.metrics.cluster import adjusted_rand_score
from contactclassification.relationshiptype import RelationshipType
from analysis.crossmatrixanalysis import CHOSEN_FEATURES

os.chdir(initial_dir)

def kmeans_missing(X, k, max_iter):
    """
    Performs K-Means clustering on data with missing values.

    Parameters
    ----------
    X: np.ndarray
        An [n_samples, n_features] array of data to cluster.
    k: int
        Number of clusters to form.
    max_iter: int
        Maximum number of iterations to perform.

    Returns
    -------
    labels: np.ndarray
        An [n_samples] vector of integer labels.
    X_filled: np.ndarray
        Copy of X with the missing values filled in.

    """

    # Initialize missing values to their column means
    missing = ~np.isfinite(X)
    mu = np.nanmean(X, 0, keepdims=1)
    X_filled = np.where(missing, mu, X)
    
    i = 1
    km = KMeans(init='random', n_clusters=k)
    km.fit(X_filled)
    prev_labels = km.labels_
    prev_centroids = km.cluster_centers_
    
    X_filled[missing] = prev_centroids[prev_labels][missing]
    converge = False
    
    while i < max_iter and not(converge):
        # Execute K-Means with the previous centroids
        km = KMeans(init = prev_centroids, n_clusters = k, n_init = 1)
        km.fit(X_filled)
        
        labels = km.labels_
        centroids = km.cluster_centers_
        
        # Fill in the missing values based on their clusters centroids
        X_filled[missing] = centroids[labels][missing]
        
        converge = np.all(labels == prev_labels)
        
        if not(converge):
            prev_labels = labels
            prev_centroids = centroids
            i += 1

    return labels, X_filled

def study_kmeans_silhouette_score(name, normalized, relationship = None):
    """
    Obtains the Silhouette score (by using K-Means algorithm) of the data and 
    save it as an image.
    
    Parameters
    ----------
    name: str
        Name of the image which is going to be saved.
    normalized: pd.DataFrame
        DataFrame which is going to be studied.
    relationship : pd.DataFrame
        DataFrame of the relationship type of each message.
        
    Returns
    -------
    None.

    """
    silhouette = np.zeros(K_MAX - 2)
    X = normalized.to_numpy()
    if relationship is not None:
        relationship.map(lambda x : RelationshipType[x].value)
        ari = []
    
    for k in range(2, K_MAX):
        labels, X_filled = kmeans_missing(X, k, MAX_ITER)
        silhouette[k-2] = silhouette_score(X_filled, labels)
        if relationship is not None:
            ari.append(adjusted_rand_score(relationship, labels))
        
    plt.figure()
    plt.plot(range(2, K_MAX), silhouette)
    plt.title('Silhouette score with K-Means for different k')
    plt.savefig(name + 'kmeans_silhouette_score.png')
    
    if relationship is not None:
        plt.figure()
        plt.plot(range(2, K_MAX), ari)
        plt.title('Adjusted Rand Score with K-Means for different k')
        plt.savefig(name + 'kmeans_ari.png')
    
def dbanalysis(X, epsilon, metric):
    """
    Executes DBSCAN algorithm.
    
    Parameters
    ----------
    X: np.ndarray
        An [n_samples, n_features] array of data to cluster.
    epsilon: float
        Distance threshold for DBSCAN.
    metric: str
        Metric fo DBSCAN.
        
    Returns
    -------
    silhouette: float
        Silhouette score.
    n_clusters_: int
        Number of final clusters.
    
    """
    n0 = 3 # Fijamos el número de elementos mínimos
    db = DBSCAN(eps=epsilon, min_samples=n0, metric=metric).fit(X)
    labels = db.labels_
    # Number of clusters in labels, ignoring noise if present.
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    silhouette = -1
    if n_clusters_ > 1:
        silhouette = silhouette_score(X, labels)

    return silhouette, n_clusters_, labels

def study_dbscan_silhouette_score(name, normalized, relationship):
    """
    Obtains the Silhouette score (by using DBSCAN algorithm) of the data and 
    save it as an image.
    
    Parameters
    ----------
    name: str
        Name of the image which is going to be saved.
    normalized: pd.DataFrame
        DataFrame which is going to be studied.
    relationship : pd.DataFrame
        DataFrame of the relationship type of each message.

    Returns
    -------
    None.

    """
    X = replace_nan(normalized, relationship)
    
    relationship.map(lambda x : RelationshipType[x].value)
    
    metrics = ['euclidean', 'manhattan']
    
    for m in metrics:
        maxS = -1
        epsiOpt = 0
        silhouettes = []
        num_clust = []
        ari = []
        interval = np.arange(0.01, 1, 0.01)
        
        for epsilon in interval:
            s, n, labels = dbanalysis(X, epsilon, m)
            silhouettes.append(s)
            num_clust.append(n)
            ari.append(adjusted_rand_score(relationship, labels))
            if maxS < s:
                maxS = s
                epsiOpt = epsilon

        plt.figure(figsize=(13,4))
        plt.subplot(1,2,1)
        plt.plot(interval, silhouettes)
        plt.plot([epsiOpt, epsiOpt], [-1.1, maxS+0.1], linestyle = "--")
        plt.title(r'Silhouette score for different $\varepsilon$')
        plt.xlabel(r"$\varepsilon$")
        plt.ylabel("Silhouette score")
        plt.grid()

        plt.subplot(1,2,2)
        plt.plot(interval, num_clust)
        plt.plot([epsiOpt, epsiOpt], [0, max(num_clust)], linestyle = "--")
        plt.title(r'Number of clusters for different $\varepsilon$')
        plt.xlabel(r"$\varepsilon$")
        plt.ylabel("Number of clusters")
        plt.grid()

        plt.tight_layout()
        plt.savefig(name + 'dbscan_' + m + '_silhouette_score.png')
        
        plt.figure()
        plt.plot(interval, ari)
        plt.title(r'Adjusted Rand Score with DBSCAN for different $\varepsilon$')
        plt.savefig(name + m + '_dbscan_ari.png')
        
def main():
    df = pd.read_csv('dataframe.csv')
    normalized = pd.read_csv('normalized.csv')
    
    study_kmeans_silhouette_score('norm_', normalized, df['relationship'])
    study_dbscan_silhouette_score('norm_', normalized, df['relationship'])
    study_kmeans_silhouette_score('data_', df.drop(columns = ['_id', 'relationship']),
                                  df['relationship'])
    study_dbscan_silhouette_score('data_', df.drop(columns = ['_id', 'relationship']), 
                                  df['relationship'])
    
    study_kmeans_silhouette_score('norm_8dim_', normalized[CHOSEN_FEATURES],
                                  df['relationship'])
    study_dbscan_silhouette_score('norm_8dim_', normalized[CHOSEN_FEATURES], 
                                  df['relationship'])
    study_kmeans_silhouette_score('data_8dim_', df[CHOSEN_FEATURES], df['relationship'])
    study_dbscan_silhouette_score('data_8dim_', df[CHOSEN_FEATURES], 
                                  df['relationship'])
        
if __name__ == '__main__':
    main()