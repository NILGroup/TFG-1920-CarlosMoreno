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
from sklearn import preprocessing
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

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
    
def study_silhouette_score(normalized):
    silhouette = np.zeros(cf.K_MAX - 2)
    for k in range(2, cf.K_MAX): 
        km = KMeans(init='random', n_clusters=k)
        km.fit(normalized)
        
        silhouette[k-2] = silhouette_score(normalized, km.labels_)
        
    plt.plot(range(2, cf.K_MAX), silhouette)
    plt.title('Silhouette score for different k')
    plt.savefig('silhouette_score.png')
    
def generate_colors():
    """
    Generates a dictionary of colours which determines the colour of each
    relationship type.

    Returns
    -------
    dic_colors : dict
        Dictionary which relates each relationship type with a colour.

    """
    colors = np.linspace(0, 1, num = len(RelationshipType))
    dic_colors = {}
    for t in RelationshipType:
        dic_colors[t.name] = str(colors[t.value - 1])
    return dic_colors

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
    
    normalized = preprocessing.normalize(np.array(df.drop(columns = 
                                                          ['_id', 'relationship'])).T).T
    # normalized.to_csv('normalized.csv')
    # normalized = pd.read_csv('normalized.csv')
    study_silhouette_score(normalized)
    
    dic_colors = generate_colors()
    colors = df['relationship'].map(dic_colors)
    scatter_matrix(normalized, figsize = (20, 20), diagonal = 'hist', color=colors)
    plt.savefig('scatter_matrix.png')
    
if __name__ == '__main__':
    main()