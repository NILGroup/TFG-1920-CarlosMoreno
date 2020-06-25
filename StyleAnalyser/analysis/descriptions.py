# -*- coding: utf-8 -*-
"""
Created on Thu May 21 22:37:25 2020

@author: Carlos Moreno Morera
"""
import os, sys
initial_dir = os.getcwd()
os.chdir('../')
if not(os.getcwd() in sys.path):
    sys.path.append(os.getcwd())

import pandas as pd
from pandas.plotting import table
import matplotlib.pyplot as plt
from contactclassification.relationshiptype import RelationshipType
from analysis.crossmatrixanalysis import CHOSEN_FEATURES

os.chdir(initial_dir)

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

    plt.figure(figsize = (30, 20))
    plot = plt.subplot(111, frame_on=False)

    plot.xaxis.set_visible(False) 
    plot.yaxis.set_visible(False) 

    table(plot, desc,loc='upper right')
    plt.savefig(name + '.png')

def main():
    df = pd.read_csv('dataframe.csv')
    normalized = pd.read_csv('normalized.csv')
    
    os.mkdir('data/')
    os.chdir('data/')
    describe_dataframe(df, 'general_description')
    for t in RelationshipType:
        describe_dataframe(df[df.relationship.eq(t.name)], t.name + '_description')
    os.chdir('../')
        
    os.mkdir('norm/')
    os.chdir('norm/')
    describe_dataframe(normalized, 'general_description')
    for t in RelationshipType:
        describe_dataframe(normalized[df.relationship.eq(t.name)], t.name + '_description')
    os.chdir('../')
        
    os.mkdir('data_8dim/')
    os.chdir('data_8dim/')
    describe_dataframe(df[CHOSEN_FEATURES], 'general_description')
    for t in RelationshipType:
        describe_dataframe(df[CHOSEN_FEATURES][df.relationship.eq(t.name)], 
                           t.name + '_description')
    os.chdir('../')
    
    os.mkdir('norm_8dim/')
    os.chdir('norm_8dim/')
    describe_dataframe(normalized[CHOSEN_FEATURES], 'general_description')
    for t in RelationshipType:
        describe_dataframe(normalized[CHOSEN_FEATURES][df.relationship.eq(t.name)], 
                           t.name + '_description')
    os.chdir('../')
        
if __name__ == '__main__':
    main()