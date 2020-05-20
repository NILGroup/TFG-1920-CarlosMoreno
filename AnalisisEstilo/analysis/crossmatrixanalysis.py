# -*- coding: utf-8 -*-
"""
Created on Wed May 20 15:53:29 2020

@author: Carlos Moreno Morera
"""
import os, sys
initial_dir = os.getcwd()
os.chdir('../')
if not(os.getcwd() in sys.path):
    sys.path.append(os.getcwd())

import pandas as pd
from pandas.plotting import scatter_matrix
from analysis.treeanalysis import replace_nan
import matplotlib.pyplot as plt
from contactclassification.relationshiptype import RelationshipType
from analysis.confanalysis import COLORS
import seaborn as sns
import numpy as np

os.chdir(initial_dir)

CHOSEN_FEATURES = ['verbAdjectiveRatio', 'detPronRatio', 'meanSentLen',
                   'meanWordLen', 'richnessYule', 'difficultyLevel',
                   'stopRatio', 'entropy']

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
        dic_colors[t.name] = str(COLORS[t.value - 1])
    return dic_colors

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
    
def get_correlation_matrix(df, relationship):
    """
    Obtains the correlation matrix of the given DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Data which is going to be studied.
    relationship : pd.DataFrame
        DataFrame of the relationship type of each message.

    Returns
    -------
    None.

    """
    X = replace_nan(df, relationship)
    plt.figure()
    cor = np.corrcoef(X)
    sns.heatmap(cor, annot=True, cmap=plt.cm.Reds)
    plt.savefig('correlation_matrix.png')

def main():
    df = pd.read_csv('dataframe.csv')
    normalized = pd.read_csv('normalized.csv')
    
    get_correlation_matrix(normalized, df['relationship'])
    get_scatter_matrix('norm_8_dim_', normalized[CHOSEN_FEATURES], 
                       df['relationship'])
    
if __name__ == '__main__':
    main()