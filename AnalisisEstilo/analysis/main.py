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
import pandas as pd
import json
from pandas.plotting import scatter_matrix
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier, export_graphviz
from sklearn.tree import _tree
from analysis.treeanalysis import calculate_features_importance
from analysis.treeanalysis import replace_nan, calculate_best_depth
from analysis.clustering import study_kmeans_silhouette_score
from analysis.clustering import study_dbscan_silhouette_score
from analysis.crossmatrixanalysis import generate_colors
from analysis.descriptions import describe_dataframe

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

def get_scatter_matrix(name, normalized, relationship):
    """
    Obtains the scatter matrix of the data set.

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
    
    dic_colors = generate_colors()
    colors = relationship.map(dic_colors)
    scatter_matrix(pd.DataFrame(X), figsize = (100, 100), diagonal = 'hist', 
                   color=colors)
    plt.savefig(name + 'scatter_matrix.png')
    
def pca_analysis(df, relationship, name):
    """
    Executes a PCA analysis with the given DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame which is going to be studied.
    relationship : pd.DataFrame
        DataFrame of the relationship type of each message.
    name: str
        Name of the image which is going to be saved.

    Returns
    -------
    None.

    """
    X = replace_nan(df, relationship)
    X = StandardScaler().fit_transform(X)
    X = pd.DataFrame(data = X, columns = df.columns)
    labels = df.columns
    
    for n in range(1, cf.N_COMPONENTS + 1):
        pca = PCA(n_components = n)
        pca.fit(X)
               
        os.mkdir(name + 'PCA' + str(n) + '/')
        os.chdir(name + 'PCA' + str(n) + '/')
        with open('expvar.json', 'a') as f:
            f.write(json.dumps(pca.explained_variance_ratio_.tolist()))
        pd.DataFrame(pca.components_, columns = labels).to_csv(f'pca{n}.csv', 
                                                                    index = False)
        for i in range(n):
            comi = pca.components_[i].copy()
            comiabs = list(map(lambda x: abs(x), comi))
            total = sum(comiabs)
            comiabs = list(map(lambda x: (x/total) * 100, comiabs))
            
            plt.figure()
            patches, _ = plt.pie(comiabs, colors=cf.COLORS[:len(labels)], shadow=True,
                                     startangle=90)
            
            for j in range(len(comi)):
                if comi[j] < 0:
                    patches[j].set_hatch('/')
            plt.legend(patches, prop={'size': 6}, labels = ['%s, %1.1f %%' % (l, s) 
                                          for l, s in zip(labels, comiabs)], loc="best")
            plt.axis('equal')
            plt.title('Component with '+ '%.4f'%(pca.explained_variance_ratio_[i])
                      + ' of explained variance ratio')
            plt.tight_layout()
            plt.savefig('comp' + str(i) + '_pie.png')
            
        os.chdir('../')
        
def tree_to_list(node, depth, tree_, feature_name, final_list):
    """
    Recursive method which transforms the given decision tree to a list.

    Parameters
    ----------
    node : int
        Node which is going to be transformed.
    depth : int
        Depth of the node.
    tree_ : sklearn.tree._tree.Tree
        Tree which is going to be trasnformed.
    feature_name : list
        List of strings with the names of the features of the initial DataFrame.
    final_list : list
        Result of the transformation.

    Returns
    -------
    None.

    """
    if len(final_list) < depth:
        final_list.append({})
    if tree_.feature[node] != _tree.TREE_UNDEFINED:
        if feature_name[node] in final_list[depth - 1]:
            final_list[depth - 1][feature_name[node]] += 1
        else:
            final_list[depth - 1][feature_name[node]] = 1
            
        tree_to_list(tree_.children_left[node], depth + 1, tree_, feature_name,
                     final_list)
        tree_to_list(tree_.children_right[node], depth + 1, tree_, feature_name,
                     final_list)

def tree_to_json(tree, feature_names, name):
    """
    Transforms the given decision tree to a json and saves it.

    Parameters
    ----------
    tree : sklearn.tree._classes.DecisionTreeClassifier
        Tree which is going to be transformed.
    feature_names : list
        List of the names of the features of the initial DataFrame.
    name : str
        Name of the file which is going to be saved.

    Returns
    -------
    None.

    """
    tree_ = tree.tree_
    feature_name = [feature_names[i] if i != _tree.TREE_UNDEFINED else "undefined!"
        for i in tree_.feature]
    final_list = []
    tree_to_list(0, 1, tree_, feature_name, final_list)
    with open(name + '_tree.json', 'a') as f:
        f.write(json.dumps(final_list))

def classify_with_decission_tree(df, relationship, criteria, name):
    """
    Generates the decision tree of the given data.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame which is going to be studied.
    relationship : pd.DataFrame
        DataFrame of the relationship type of each message.
    criteria : str
        Criteria for generating it ('gini' or 'entropy').
    name: str
        Name of the image which is going to be saved.

    Returns
    -------
    None.

    """
    X = replace_nan(df, relationship)
    depth = calculate_best_depth(X, relationship, name, criteria)
    
    clf = DecisionTreeClassifier(criterion=criteria, splitter="best",
                             max_depth=depth)
    clf = clf.fit(X, relationship)
    export_graphviz(clf, out_file= name + criteria +'_tree.dot', 
                    feature_names=df.columns, class_names=
                    [t.name for t in RelationshipType], filled=True, rounded=True,  
                     special_characters=True)
    
    tree_to_json(clf, df.columns, name + criteria)
    calculate_features_importance(clf, df.columns, name + criteria)

def main():
    init_db()
    df = pd.DataFrame([without_keys(m, cf.UNUSED_FIELDS) for m in 
                       json.loads(Metrics.objects().to_json())])
    df.set_index('_id')
    transform_recipients_columns(df)
    # df.to_csv('dataframe.csv', index = False)
    # df = pd.read_csv('dataframe.csv')
    
    describe_dataframe(df, 'general_description')
    for t in RelationshipType:
        describe_dataframe(df[df.relationship.eq(t.name)], t.name + '_description')
    
    normalized = df.drop(columns = ['_id', 'relationship'])
    cols = list(normalized.columns.values)
    for c in cols:
        normalized[c]=(df[c]-df[c].min())/(df[c].max()-df[c].min())
        
    # normalized.to_csv('normalized.csv', index = False)
    # normalized = pd.read_csv('normalized.csv')
    study_kmeans_silhouette_score('norm_', normalized)
    study_dbscan_silhouette_score('norm_', normalized, df['relationship'])
    get_scatter_matrix('norm_', normalized, df['relationship'])
    
    study_kmeans_silhouette_score('data_', df.drop(columns = ['_id', 'relationship']))
    study_dbscan_silhouette_score('data_', df.drop(columns = ['_id', 'relationship']), 
                                  df['relationship'])
    get_scatter_matrix('data_', df.drop(columns = ['_id', 'relationship']), 
                       df['relationship'])
    
    pca_analysis(normalized, df['relationship'], 'norm_')
    pca_analysis(df.drop(columns = ['_id', 'relationship']), df['relationship'],
                 'data_')
    
    for c in ['gini', 'entropy']:
        classify_with_decission_tree(df.drop(columns = ['_id', 'relationship']),
                                     df['relationship'], c, 'data_')
        classify_with_decission_tree(normalized, df['relationship'], c, 'norm_')
    
if __name__ == '__main__':
    main()