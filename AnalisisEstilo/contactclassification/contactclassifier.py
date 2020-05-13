# -*- coding: utf-8 -*-
"""
Created on Mon May 11 18:50:32 2020

@author: Carlos
"""
import os, sys
initial_dir = os.getcwd()
os.chdir('../')
if not(os.getcwd() in sys.path):
    sys.path.append(os.getcwd())

from initdb import init_db
from contactclassification.relationshiptype import RelationshipType
from stylemeasuring.metrics import Metrics
from contactclassification.classifiedcontact import ClassifiedContact

os.chdir(initial_dir)

def get_relationship_type(types_list):
    """
    Asks the user about the type of relationship.
    
    Parameters
    ----------
    types_list: list
        List of the different types of relationship.
        
    Returns
    -------
    RelationshipType: type of relationship choosen by the user.
    
    """
    count = 0
    print('What is the type of relationship with this contact?')
    for t in types_list:
        print(f"{count}.- {t.name}")
        count += 1
        
    chosen = False
    while not chosen:
        try:
            opt = int(input('Choose an option: '))
            chosen = opt < len(types_list)
        except ValueError:
            print('Invalid input.\n')
    
    return types_list[opt]

def classify_contact(address, types_list):
    """
    Classifies the given contact and saves it in the appropiate MongoDB table.

    Parameters
    ----------
    address : str
        Given contact.
    types_list : list
        List of the different types of relationship.

    Returns
    -------
    None.

    """
    name = ''
    address = address.strip()
    ind = address.find('<')
    
    if ind == -1 and not(ClassifiedContact.objects(email = address)):
        print(f'The email address is {address}.')
        name = input("Introduce the conctact's name: ")
    elif ind != -1:
        name = address[:ind].strip()
        end = address.find('>')
        address = address[ind + 1:end].strip()
        
        ind = name.find('"')
        if ind != -1:
            name = name[ind+1:]
            name = name[:name.find('"')].strip()
            
    if not(ClassifiedContact.objects(email = address)):
        clasc = ClassifiedContact()
        clasc.email = address
        clasc.name = name
        print(f'The email address is {address}.')
        clasc.category = get_relationship_type(types_list).name
        clasc.save()

def main():
    types = []
    for t in RelationshipType:
        types.append(t)
        
    init_db()
    for m in Metrics.objects():
        for d in m.to:
            classify_contact(d, types)
        for d in m.cc:
            classify_contact(d, types)
        for d in m.bcc:
            classify_contact(d, types)
            
if __name__ == '__main__':
    main()