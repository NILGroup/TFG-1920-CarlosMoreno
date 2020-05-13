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
import analysis.confanalysis as cf
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import pandas as pd
import json
from pandas.plotting import scatter_matrix

os.chdir(initial_dir)

def without_keys(d, keys):
    return {x: d[x] for x in d if x not in keys}

def convert_recipients_to_relationship_type(to, cc, bcc):
    if len(to) + len(cc) + len(bcc) == 1:
        l = to if len(to) == max(map(len, [to, cc, bcc])) else (
            cc if len(cc) > len(bcc) else bcc)
        return ClassifiedContact.objects(email = l[0]).first().category
    elif len(to) == 1:
        return ClassifiedContact.objects(email = to[0]).first().category
    
    num_types = np.zeros(len(RelationshipType))
    recipients = [to, cc, bcc]
    for l in recipients:
        for address in l:
            t = ClassifiedContact.objects(email = address).first().category
            num_types[RelationshipType[t].value] += 1
            
    existing_types = np.where(num_types > 0)
    
    if len(existing_types) == 1:
        return RelationshipType(existing_types[0]).name
    
    print('The email has the following recipients:')
    recipients_str = ['', '', '']
    for i in range(len(recipients)):
        for address in recipients[i]:
            recipients_str[i] += address
            recipients_str[i] += ' '
    
    print(f'To: {recipients_str[0]}')
    print(f'Cc: {recipients_str[1]}')
    print(f'Bcc: {recipients_str[2]}')
    
    print('What is the type of relationship of this email?')    
    return get_relationship_type()

def transform_recipients_columns(df):
    df['relationship'] = df.apply(lambda row : 
                                  convert_recipients_to_relationship_type(
                                      row['to'], row['cc'], row['bcc']))
    df.drop(columns = ['to', 'cc', 'bcc'], inplace = True)

def main():
    init_db()
    df = pd.DataFrame([without_keys(m, cf.UNUSED_FIELDS) for m in 
                       json.loads(Metrics.objects().to_json())])
    df.set_index('_id')
    
if __name__ == '__main__':
    main()