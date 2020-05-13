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

def get_relationship_type():
    """
    Asks the user about the type of relationship.
        
    Returns
    -------
    str: type of relationship choosen by the user.
    
    """
    for i in range(len(RelationshipType)):
        print(f'{i}.- {RelationshipType(i).name}')
        
    chosen = False
    while not chosen:
        try:
            opt = int(input('Choose an option: '))
            chosen = opt < len(RelationshipType)
        except ValueError:
            print('Invalid input.\n')
    
    return RelationshipType(opt).name

def classify_contact(address):
    """
    Classifies the given contact and saves it in the appropiate MongoDB table.

    Parameters
    ----------
    address : str
        Given contact.

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
        print('What is the type of relationship with this contact?')
        clasc.category = get_relationship_type()
        clasc.save()

def main():        
    init_db()
    for m in Metrics.objects():
        for l in [m.to, m.cc, m.bcc]:
            for d in l:
                classify_contact(d)
            
if __name__ == '__main__':
    main()