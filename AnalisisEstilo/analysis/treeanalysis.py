# -*- coding: utf-8 -*-
"""
Created on Tue May 19 21:24:35 2020

@author: Carlos Moreno Morera
"""
import os, sys
initial_dir = os.getcwd()
os.chdir('../')
if not(os.getcwd() in sys.path):
    sys.path.append(os.getcwd())

import json
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sklearn.tree import _tree
from contactclassification.relationshiptype import RelationshipType
from analysis.confanalysis import MAX_DEPTH, COLORS
from sklearn.tree import DecisionTreeClassifier, export_graphviz
from sklearn.model_selection import cross_validate
from sklearn.model_selection import train_test_split
from analyser import yes_no_question

os.chdir(initial_dir)

def replace_nan(df, relationship):
    """
    Replaces NaN values in the given DataFrame

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame which is going to be changed.
    relationship : pd.DataFrame
        DataFrame of the relationship type of each message.

    Returns
    -------
    X : np.ndarray
        Data without NaN values.

    """
    X = df.to_numpy()
    for t in RelationshipType:
        category = relationship == t.name
        missing_cat = ~np.isfinite(X[category])
        mu = np.nanmean(X[category], 0, keepdims=1)
        X[category] = np.where(missing_cat, mu, X[category])
        
    return X

def tree_to_feature_importance(node, tree_, feature_name, feat_imp):
    """
    Calculates the importance of each feature.

    Parameters
    ----------
    node : int
        Number of the node which is being analysed.
    tree_ : sklearn.tree._tree.Tree
        Tree which provide us the information.
    feature_names : list
        List of the names of the features of the initial DataFrame.
    feat_imp : dict
        Dictionary which relates each features with its importance.

    Returns
    -------
    float
        Importance of all nodes.

    """
    if tree_.feature[node] != _tree.TREE_UNDEFINED:
        name = feature_name[node]
        
        if name not in feat_imp:
            feat_imp[name] = 0
        
        node_imp = tree_.weighted_n_node_samples[node] * tree_.impurity[node]
        l_node = tree_.children_left[node]
        r_node = tree_.children_right[node]
        node_imp -= tree_.weighted_n_node_samples[l_node] * tree_.impurity[l_node]
        node_imp -= tree_.weighted_n_node_samples[r_node] * tree_.impurity[r_node]
        feat_imp[name] += node_imp
        
        l_imp = tree_to_feature_importance(l_node, tree_, feature_name, feat_imp)
        r_imp = tree_to_feature_importance(r_node, tree_, feature_name, feat_imp)
        
        return node_imp + l_imp + r_imp
    else:
        return 0
        
def calculate_features_importance(tree, feature_names, name = 'tree'):
    """
    Calculates the importance of each feature and saves this information in a
    json file.

    Parameters
    ----------
    tree_ : sklearn.tree._tree.Tree
        Tree which provide us the information.
    feature_names : list
        List of the names of the features of the initial DataFrame.
    name : str
        Name of the file which is going to be saved. The default value is 'tree'.

    Returns
    -------
    None.

    """
    tree_ = tree.tree_
    feature_name = [feature_names[i] if i != _tree.TREE_UNDEFINED else "undefined!"
        for i in tree_.feature]
    features_importance = {}
    total_imp = tree_to_feature_importance(0, tree_, feature_name, features_importance)
    
    for k in features_importance:
        features_importance[k] = features_importance[k]/total_imp
    
    with open(name + '_feat_imp.json', 'a') as f:
        f.write(json.dumps(features_importance))
        
    labels = [k for k in features_importance]
    sizes = [features_importance[k] * 100 for k in features_importance]
    plt.figure()
    patches, texts = plt.pie(sizes, colors=COLORS[:len(labels)], shadow=True,
                             startangle=90)
    plt.legend(patches, prop={'size': 6}, labels = ['%s, %1.1f %%' % (l, s) 
                                  for l, s in zip(labels, sizes)], loc="best")
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig(name + '_pie.png')
        
def calculate_best_depth(X, relationship, name = 'tree', criteria = 'entropy'):
    """
    Calculates the best depth based on the learning curve.

    Parameters
    ----------
    X : np.ndarray
        Set of data.
    relationship : pd.DataFrame
        DataFrame of the relationship type of each message.
    criteria : str
        Criteria for generating it ('gini' or 'entropy'). The default value
        is 'entropy'.
    name: str
        Name of the image which is going to be saved. The default value is 'tree'.

    Returns
    -------
    depth : int
        Best depth.

    """
    train_accuracy = []
    test_accuracy = []
    max_train = 0
    max_test = 0
    depth = 0
    
    for md in range(1, MAX_DEPTH):
        clf = DecisionTreeClassifier(criterion=criteria, max_depth=md)
        scores = cross_validate(clf, X, relationship, scoring='accuracy', cv=10, 
                                return_train_score=True)
        
        train_accuracy.append(np.mean(scores['train_score']))
        test_accuracy.append(np.mean(scores['test_score']))
        
        if (0.9 < train_accuracy[-1] and 1 > train_accuracy[-1] and 
            (max_test < test_accuracy[-1] or (max_test == test_accuracy[-1] and
                                              max_train < train_accuracy[-1]))):
            max_test = test_accuracy[-1]
            max_train = train_accuracy[-1]
            depth = md
            
    plt.figure()
    # Draw lines
    plt.plot(range(1, MAX_DEPTH), train_accuracy, '-o', color="r",  label="Training")
    plt.plot(range(1, MAX_DEPTH), test_accuracy, '-o', color="g", label="Test")
    
    # Create plot
    plt.title("Learning curve")
    plt.xlabel("Parameter"), plt.ylabel("Accuracy Score"), plt.legend(loc="best")
    plt.tight_layout()
    plt.grid()
    plt.savefig(name + criteria + '_learning_curve.png')
            
    return depth
        
def generate_decision_tree(df, relationship, name = 'tree'):
    """
    Generates a decision tree and study the importance of each feature in it.

    Parameters
    ----------
    df : pd.DataFrame
        Set of data.
    relationship : pd.DataFrame
        DataFrame of the relationship type of each message.
    name : str
        Name of the files which are going to be saved. The default value is 'tree'.

    Returns
    -------
    None.

    """
    X = replace_nan(df, relationship)
    depth = calculate_best_depth(X, relationship, name, 'entropy')
    clf = DecisionTreeClassifier(criterion='entropy', splitter="best",
                             max_depth=depth)
    clf = clf.fit(X, relationship)
    export_graphviz(clf, out_file= name + '_tree.dot', 
                    feature_names=df.columns, class_names=
                    [t.name for t in RelationshipType], filled=True, rounded=True,  
                     special_characters=True)
    calculate_features_importance(clf, df.columns, name)
    
def get_deleted_features():
    """
    Asks for the features that the user wants to remove.

    Returns
    -------
    del_col : list
        List of the names of features that the user wants to remove.

    """
    del_col = []
    c = input('Introduce the name of the column which is going to be deleted: ')
    del_col.append(c)
    while(yes_no_question('Do you want to delete more columns?')):
        c = input('Introduce the name of the column which is going to be deleted: ')
        del_col.append(c)
        
    with open('del_features.json', 'a') as f:
        f.write(json.dumps(del_col))
    return del_col

def drop_unimportant_features(df, name = 'tree'):
    """
    Removes the features of the DataFrame which have an importance with value
    0.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame from which the unimportant features are going to be removed.
    name : str
        Name of the file where the importance of each feature has been saved.
        The default value is 'tree'.

    Returns
    -------
    None.

    """
    feat_imp = None
    
    with open(name + '_feat_imp.json', 'r') as f:
        feat_imp = json.loads(f.read())
    
    del_col = []
    for c in df.columns:
        if c not in feat_imp:
            del_col.append(c)
            
    with open('unimportant_features.json', 'a') as f:
        f.write(json.dumps(del_col))            
    df.drop(columns = del_col, inplace = True)

def main():
    df = pd.read_csv('dataframe.csv')
    normalized = pd.read_csv('normalized.csv')
    num_del_feats = []
    feat_imp = {}
    initial_feats = len(normalized.columns)
    
    while(yes_no_question('Do yo want to continue?')):
        num_del_feats.append(initial_feats - len(normalized.columns))
        os.mkdir(str(len(normalized.columns)) + 'feat/')
        os.chdir(str(len(normalized.columns)) + 'feat/')
        
        generate_decision_tree(normalized, df['relationship'])
        drop_unimportant_features(normalized)
        del_feat = get_deleted_features()
        normalized.drop(columns = del_feat, inplace = True)
        
        with open('tree_feat_imp.json', 'r') as f:
            feat_imp_aux = json.loads(f.read())
            
        for k in feat_imp_aux:
            if k not in feat_imp:
                feat_imp[k] = []
            feat_imp[k].append(feat_imp_aux[k] * 100)
        
        os.chdir('../')
    
    color_ind = 0
    plt.figure()
    for k in feat_imp:
        plt.plot(num_del_feats[:len(feat_imp[k])], feat_imp[k], '-o', 
                 color=COLORS[color_ind], label=k)
        color_ind += 1
        
    plt.title("Importance curve")
    plt.xlabel("Number of deleted features")
    plt.ylabel("Importance")
    plt.legend(bbox_to_anchor = (1.04, 1), loc="upper left", prop={'size': 6})
    plt.tight_layout()
    plt.grid()
    plt.savefig('importance_curve.png')

if __name__ == '__main__':
    main()