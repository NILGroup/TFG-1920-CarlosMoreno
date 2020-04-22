# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 14:32:54 2019

@author: Carlos Moreno Morera
"""

from __future__ import print_function
from googleapiclient.discovery import build
import config
import auth
from analyser import Analyser
import os
import sys

def yes_no_question(question):
        """
        Asks the user the given yes or no question.
        
        Parameters
        ----------
        question: str
            Question which is going to be asked.
        
        Returns
        -------
        bool: true if the answer is yes and false if it is not.
        
        """
        answ = input(f'\n{question} [y/n] ')
        while(not answ in {'y', 'n'}):
            print('Please write "y" or "n" to answer the question.\n')
            answ = input(f'{question} [y/n] ')
            
        return answ == 'y'

def main():
    """
    Analyse the emails of the user and obtain the style metrics
    """
    if not(os.getcwd() in sys.path):
        sys.path.append(os.getcwd())
    
    #Creation of a Gmail resource
    service = build('gmail', 'v1',
                    credentials = auth.get_credentials(config.SCOPES, config.CREDS))
    anls = None
    nextPageToken = None
    if (yes_no_question('Were there a previous execution with the same credentials?')):
        q = int(input('Introduce the remaining quota units: '))
        if (yes_no_question('Was it with the same user?')):
            ext = yes_no_question('Was the previously executed by extracting messages?')
            nextPageToken = input('Introduce NextPageToken: ')
            num_res = int(input('How many Gmail resources were extracted? '))
            anls = Analyser(service, q, ext, num_res)
        else:
            anls = Analyser(service, q)
    else:
        anls = Analyser(service)
        
    if (yes_no_question('Has the user an email signature?')):
        print('Introduce the signature and finish it with the word "STOP".\n')
        entr = input()
        sign = ''
        while (entr != 'STOP'):
            sign += entr + '\n'
            entr = input()
        anls.analyse(nextPageToken, sign)
    else:
        anls.analyse(nextPageToken)

if __name__ == '__main__':
    main()