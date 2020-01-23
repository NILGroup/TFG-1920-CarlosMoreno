# -*- coding: utf-8 -*-
"""
Created on Thu Jan 23 16:17:23 2020

@author: Carlos Moreno Morera
"""

from __future__ import print_function

class StyleMeter:
    
    def __init__(self, corrected, cor_cv, typo_fin, nlp):
        """
        Class constructor.

        Parameters
        ----------
        corrected : list
            List of preprocessed messages whose typographical errors have been 
            corrected.
        cor_cv : multiprocessing.Condition
            Conditional variable for accessing to corrected.
        typo_fin : multiprocessing.Event
            Event which informs whether or not the typographic correction of messages 
            has finished.
        nlp : spacy model
            Spacy's trained model which will be used to processed.

        Returns
        -------
        Constructed StyleMeter class.

        """
        self.corrected = corrected
        self.cor_cv = cor_cv
        self.typo_fin = typo_fin
        self.nlp = nlp