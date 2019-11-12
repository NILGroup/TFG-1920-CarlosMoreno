# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 14:32:54 2019

@author: Carlos Moreno Morera
"""

from __future__ import print_function
from googleapiclient.discovery import build
import config
import auth
import analyser

def main():
    """
    Analyse the emails of the user and obtain the style metrics
    """
    #Creation of a Gmail resource
    service = build('gmail', 'v1',
                    credentials = auth.get_credentials(config.SCOPES, config.CREDS))


if __name__ == '__main__':
    main()