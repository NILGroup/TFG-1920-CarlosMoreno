# -*- coding: utf-8 -*-
"""
Created on Wed May 13 18:38:53 2020

@author: Carlos Moreno Morera
"""

import os, sys
initial_dir = os.getcwd()
os.chdir('../')
if not(os.getcwd() in sys.path):
    sys.path.append(os.getcwd())

from initdb import init_db
from stylemeasuring.metrics import Metrics
from contactclassification.classifiedcontact import ClassifiedContact
from contactclassification.relationshiptype import RelationshipType
from contactclassification.contactclassifier import get_relationship_type
import base64
from typocorrection.correctedmessage import CorrectedMessage
import analysis.confanalysis as cf
import numpy as np
import matplotlib.pyplot as plt
from pandas.plotting import table
import pandas as pd
import json
from pandas.plotting import scatter_matrix
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.cluster import DBSCAN

os.chdir(initial_dir)

def without_keys(d, keys):
    """
    Remove the keys from the given dictionary.

    Parameters
    ----------
    d : dict
        Dictionary from which the keys are going to be removed.
    keys : set
        Set of keys that are going to be removed.

    Returns
    -------
    dict
        d without keys.

    """
    return {x: d[x] for x in d if x not in keys}

def get_email(address):
    """
    Given a recipient extracts the email.

    Parameters
    ----------
    address : str
        Recipient of the message.

    Returns
    -------
    address : str
        Email of the recipient.

    """
    address = address.strip()
    ind = address.find('<')
    
    if ind != -1:
        end = address.find('>')
        address = address[ind + 1:end].strip()
    return address

def convert_recipients_to_relationship_type(to, cc, bcc, ide):
    """
    Converts the list of recipients in a relationship type.

    Parameters
    ----------
    to : list
        List of direct message's recipients.
    cc : list
        List of message's recipients who recieved the message as a copy of the
        information sent to the recipients in 'to' attributte.
    bcc : list
        List of message's recipients who recieved the message as a copy of the
        information sent to the recipients in 'to' attributte. Each bcc 
        addressee is hidden from the rest of recipients.
    ide: str
        Identifier of the email.

    Returns
    -------
    str
        Type of relationship between the the recipients and the sender.

    """
    if len(to) + len(cc) + len(bcc) == 1:
        l = to if len(to) == max(map(len, [to, cc, bcc])) else (
            cc if len(cc) > len(bcc) else bcc)
        return ClassifiedContact.objects(email = get_email(l[0])).first().category
    elif len(to) == 1:
        return ClassifiedContact.objects(email = get_email(to[0])).first().category
    
    num_types = np.zeros(len(RelationshipType) + 1)
    for l in [to, cc, bcc]:
        for address in l:
            t = ClassifiedContact.objects(email = get_email(address)).first().category
            num_types[RelationshipType[t].value] += 1
            
    existing_types = np.where(num_types > 0)[0]
    
    if len(existing_types) == 1:
        return RelationshipType(existing_types[0]).name
    
    print('The email has the following recipients:')
    
    print(f'To: {to}')
    print(f'Cc: {cc}')
    print(f'Bcc: {bcc}')
    
    print('This is the body of the email:')
    print(base64.urlsafe_b64decode(
        CorrectedMessage.objects(msg_id = ide).first().bodyBase64Plain.encode()).decode())
    
    print('What is the type of relationship of this email?')
    return get_relationship_type()

def transform_recipients_columns(df):
    """
    Transforms the given dataframe by removing the recipients columns and
    appending a column which describes the relationship type of the message.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame that is going to be changed.

    Returns
    -------
    None.

    """
    df['to'].fillna({}, inplace = True)
    df['cc'].fillna({}, inplace = True)
    df['bcc'].fillna({}, inplace = True)
    df['relationship'] = df.apply(lambda row : 
                                  convert_recipients_to_relationship_type(
                                      row['to'], row['cc'], row['bcc'], row['_id'])
                                  , axis = 1)
    df.drop(columns = ['to', 'cc', 'bcc'], inplace = True)
    
def describe_dataframe(df, name):
    """
    Obtains the basic statistical descriptors for the given DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame from which is going to be obtained the information.
    name : str
        Name of the DataFrame.

    Returns
    -------
    None.

    """
    desc = df.describe()
    desc.to_csv(name + '.csv')

    plot = plt.subplot(111, frame_on=False)

    plot.xaxis.set_visible(False) 
    plot.yaxis.set_visible(False) 

    table(plot, desc,loc='upper right')
    plt.savefig(name + '.png')
    
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
    
def study_kmeans_silhouette_score(normalized):
    """
    Obtains the Silhouette score of the data and save it as an image.
    
    Parameters
    ----------
    normalized: pd.DataFrame
        DataFrame which is going to be studied.
        
    Returns
    -------
    None.

    """
    np.random.seed(7)
    silhouette = np.zeros(cf.K_MAX - 2)
    X = normalized.to_numpy()
    
    for k in range(2, cf.K_MAX):
        labels, X_filled = kmeans_missing(X, k, cf.MAX_ITER)
        silhouette[k-2] = silhouette_score(X_filled, labels)
        
    plt.plot(range(2, cf.K_MAX), silhouette)
    plt.title('Silhouette score with K-Means for different k')
    plt.savefig('kmeans_silhouette_score.png')
    
def dbanalisis(X, epsilon, metric):
    """
    Función que ejecuta todo el análisis que conlleva
    aplicar el algoritmo DBSCAN.
    
    Parameters
    ----------
    X: array
        Sistema de entrada (en este caso,
        1000 elementos de dos estados).
    epsilon: float
        Umbral de distancia del algoritmo DBSCAN.

    metrica: str
        Métrica a utilizar en el algoritmo DBSCAN.
        
    Returns
    -------
    float: Coeficiente de Silhouette.
    int: Número de clusters en las etiquetas.
    object: Resultado de aplicar DBSCAN con el input anterior.
    
    """

    # Clasificación mediante el algoritmo DBSCAN
    n0 = 10 # Fijamos el número de elementos mínimos
    db = DBSCAN(eps=epsilon, min_samples=n0, metric=metric).fit(X)
    labels = db.labels_
    # Number of clusters in labels, ignoring noise if present.
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    silhouette = -1 # Prefijado a -1, que es el caso n_clusters_ == 1
    if n_clusters_ > 1:  # n_clusters puede ser también 0 si set(labels)=={-1}
        silhouette = silhouette_score(X, labels)

    return silhouette, n_clusters_, db
    
def generate_colors():
    """
    Generates a dictionary of colours which determines the colour of each
    relationship type.

    Returns
    -------
    dic_colors : dict
        Dictionary which relates each relationship type with a colour.

    """
    dic_colors = {}
    for t in RelationshipType:
        dic_colors[t.name] = str(cf.COLORS[t.value - 1])
    return dic_colors

def get_scatter_matrix(normalized, relationship):
    X = normalized.to_numpy()
    
    for t in RelationshipType:
        category = relationship == t.name
        missing_cat = ~np.isfinite(X[category])
        mu = np.nanmean(X[category], 0, keepdims=1)
        X[category] = np.where(missing_cat, mu, X[category])
    
    dic_colors = generate_colors()
    colors = relationship.map(dic_colors)
    scatter_matrix(pd.DataFrame(X), figsize = (100, 100), diagonal = 'hist', 
                   color=colors)
    plt.savefig('scatter_matrix.png')

def main():
    init_db()
    df = pd.DataFrame([without_keys(m, cf.UNUSED_FIELDS) for m in 
                       json.loads(Metrics.objects().to_json())])
    df.set_index('_id')
    transform_recipients_columns(df)
    # df.to_csv('dataframe.csv')
    # df = pd.read_csv('dataframe.csv')
    
    describe_dataframe(df, 'general_description')
    for t in RelationshipType:
        describe_dataframe(df[df.relationship.eq(t.name)], t.name + '_description')
    
    normalized = df.drop(columns = ['_id', 'relationship'])
    cols = list(normalized.columns.values)
    for c in cols:
        normalized[c]=(df[c]-df[c].min())/(df[c].max()-df[c].min())
        
    # normalized.to_csv('normalized.csv')
    # normalized = pd.read_csv('normalized.csv')
    study_kmeans_silhouette_score(normalized)
    get_scatter_matrix(normalized, df['relationship'])
    
if __name__ == '__main__':
    main()