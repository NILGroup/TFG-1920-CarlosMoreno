# -*- coding: utf-8 -*-
"""
Created on Thu Jan 23 16:17:23 2020

@author: Carlos Moreno Morera
"""

from __future__ import print_function
import os
from csv import DictWriter
import confstyle as cfs

class StyleMeter:
    
    def __init__(self, corrected, cor_cv, typo_fin):
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

        Returns
        -------
        Constructed StyleMeter class.

        """
        self.corrected = corrected
        self.cor_cv = cor_cv
        self.typo_fin = typo_fin
        
    def __initialize_metrics(self, metrics, numSentences):
        """
        Initializes the style metrics in order to being measured then.
        
        Parameters
        ----------
        metrics: dict
            Dictionary where the metrics are going to be stored.
        numSentences: int
            Number of sentences of the text.
        
        Returns
        -------
        None.
        
        """
        metrics['numStopWords'] = 0
        # Number of adverbs
        metrics['ADV'] = 0
        metrics['VERB'] = 0
        metrics['ADJ'] = 0
        # Number of prepositions
        metrics['ADP'] = 0
        metrics['NOUN'] = 0
        metrics['PRON'] = 0
        metrics['DET'] = 0
        metrics['CONJ'] = 0
        
        metrics['numCommas'] = 0
        metrics['numDots'] = 0
        metrics['numSemiColon'] = 0
        metrics['num3Dots'] = 0
        metrics['numBrackets'] = 0
        
        metrics['wordLength'] = {}
        metrics['charLength'] = 0
        metrics['numWords'] = 0
        
        met_sents = metrics.copy()
        
        metrics['sentLength'] = {}
        metrics['sentNumWords'] = {}
        # Creates a dictionary of information for each sentence
        metrics['metricsSentences'] = [met_sents for i in range(numSentences)]
        
    def __calculate_punct_metrics(self, metrics, m_sent, open_brackets, t):
        """
        Modifies the metrics dictionary according to the given token which should
        be a token punctuation.
        
        Parameters
        ----------
        metrics: dict
            Dictionary where the metrics are going to be stored.
        m_sent: dict
            Dictionary of the metrics of the sentence where the given token is.
        open_brackets: int
            Number of open and non-closed brackets found previously in the text.
        t: Spacy's Token or MyToken class
            Token which is going to be analysed.
            
        Returns
        -------
        int: open_brackets (which could be modified in the function).
        
        """
        if t.is_bracket and t.is_left_punct:
            open_brackets += 1
        elif t.is_bracket and t.is_right_punct and open_brackets > 0:
            metrics['numBrackets'] += 1
            m_sent['numBrackets'] += 1
            open_brackets -= 1
        elif t.text == '.':
            metrics['numDots'] += 1
            m_sent['numDots'] += 1
        elif t.text == ',':
            metrics['numCommas'] += 1
            m_sent['numCommas'] += 1
        elif t.text == ';':
            metrics['numSemiColon'] += 1
            m_sent['numSemiColon'] += 1
        elif t.text == '...':
            metrics['num3Dots'] += 1
            m_sent['num3Dots'] += 1
        
        return open_brackets
    
    def __calculate_word_metrics(self, metrics, m_sent, words, t):
        """
        Modifies the metrics dictionary according to the given token which should
        be a non punctuation token.
        
        Parameters
        ----------
        metrics: dict
            Dictionary where the metrics are going to be stored.
        m_sent: dict
            Dictionary of the metrics of the sentence where the given token is.
        words: dics
            Dictionary which stores how many times each word appears.
        t: Spacy's Token or MyToken class
            Token which is going to be analysed.
            
        Returns
        -------
        None.
        
        """
        if t.lemma_ != '' and not(t.lemma_ in words):
            words[t.lemma_] = 0
                    
        if not(len(t.text) in metrics['wordLength']):
            metrics['wordLength'][len(t.text)] = 0
            m_sent['wordLength'][len(t.text)] = 0
                    
        metrics['wordLength'][len(t.text)] += 1
        m_sent['wordLength'][len(t.text)] += 1
        words[t.lemma_] += 1
                    
        if t.is_stop:
            metrics['numStopWords'] += 1
            m_sent['numStopWords'] += 1
        if t.pos_ in cfs.POS:
            metrics[t.pos_] += 1
            m_sent[t.pos_] += 1
            
    def __calculate_sentence_metrics(self, metrics, m_sent, s):
        """
        Modifies the metrics dictionary according to the given sentence.
        
        Parameters
        ----------
        metrics: dict
            Dictionary where the metrics are going to be stored.
        m_sent: dict
            Dictionary of the metrics of the sentence.
        s: dics
            Dictionary which stores sentence information.
            
        Returns
        -------
        None.
        
        """
        m_sent['numWords'] = len(s['words'])
        m_sent['charLength'] = len(s['doc'].text)
            
        if not(m_sent['numWords'] in metrics['sentNumWords']):
            metrics['sentNumWords'][m_sent['numWords']] = 0
        if not(m_sent['charLength'] in metrics['sentLength']):
            metrics['sentLength'][m_sent['charLength']] = 0
                
        metrics['sentNumWords'][m_sent['numWords']] += 1
        metrics['sentLength'][m_sent['charLength']] += 1
        
    def __lambdaFK(self, metrics):
        """
        Calculates the lambda parameter of the expression of level of difficulty
        of a text, given by Dubay, W.H.(2004). The principles of readability.
        Costa Mesa, CA: Impact Information. Retrieved from
        http://files.eric.ed.gov/fulltext/ED490073.pdf
        
        Lambda is the mean of one-syllable words per 100 words. I have considered
        the words with length of 1 and 2 as one-syllable words.
        
        Parameters
        ----------
        metrics: dict
            Dictionary where the metrics are stored.
            
        Returns
        -------
        float: lambda parameter.
        
        """
        one_syllable = metrics['wordLength'][1] + metrics['wordLength'][2]
        return (one_syllable * 100)/metrics['numWords']
    
    def __Flesch_Kincaid_Index(self, metrics):
        """
        Calculates the Flesch-Kincaid index (expression which determines the level
        of difficulty of a text) given by Dubay, W.H.(2004). The principles of 
        readability. Costa Mesa, CA: Impact Information. Retrieved from
        http://files.eric.ed.gov/fulltext/ED490073.pdf
        
        Parameters
        ----------
        metrics: dict
            Dictionary where the metrics are stored.
            
        Returns
        -------
        float: Flesch-Kincaid index.
        
        """
        beta = 0
        for key in metrics['sentNumWords']:
            beta += key * metrics['sentNumWords'][key]
        
        beta = beta/len(metrics['metricsSentences'])
        
        return 1.599 * self.__lambdaFK(metrics) - 1.015 * beta - 31.517
        
    def __calculate_metrics(self, metrics, cor_msg, doc):
        self.__initialize_metrics(metrics, len(cor_msg['sentences']))
        
        words = {}
        open_brackets = 0
        ind_sent = 0
        
        for s in cor_msg['sentences']:
            m_sent = ['metricsSentences'][ind_sent]
            for t in s['words']:
                if t.is_oov:
                    cor = cor_msg['corrections'].pop(0)
                    t = cor['token']
                    
                if t.is_punct:
                    open_brackets = self.__calculate_punct_metrics(metrics, m_sent, 
                                                                   open_brackets, t)
                elif not(t.like_url or t.like_email):
                    self.__calculate_word_metrics(metrics, m_sent, words, t)
            
            self.__calculate_sentence_metrics(metrics, m_sent, s)
            ind_sent += 1
        
        metrics['numWords'] = len(doc)
        metrics['charLength'] = cor_msg['charLength']
        
        # Ril, Y., Y.C. & Fonseca, E. (2014) Determination of writing styles
        metrics['stopRatio'] = (metrics['numStopWords']/metrics['numWords']) * 100
        # Flesch-Kincaid (DuBay, 2004)
        metrics['difficultyLevel'] = self.__Flesch_Kincaid_Index(metrics)
        
    def measure_style(self, user):
        if not os.path.exists(user + '/TypoCorrection'):
            os.mkdir(user + '/TypoCorrection')
            
        if not os.path.exists(user + '/TypoCorrection/typocorrected.csv'):
            csvfile = open(user + '/TypoCorrection/typocorrected', 'w')
            writer = DictWriter(csvfile, fieldnames = cfs.CSV_COL)
            writer.writeheader()
        else:
            csvfile = open(user + '/TypoCorrection/typocorrected', 'a')
            writer = DictWriter(csvfile, fieldnames = cfs.CSV_COL)
            
        self.cor_cv.acquire()
        while (not(self.typo_fin.is_set()) or len(self.corrected) > 0):
            extracted = False
            while (len(self.corrected) == 0 and not(self.typo_fin.is_set())):
                self.cor_cv.wait()
            if (len(self.corrected) > 0):
                cor_msg = self.corrected.pop()
                extracted = True
            self.cor_cv.release()
            
            if extracted:
                metrics = {}
                del cor_msg['bodyPlain']
                doc = cor_msg.pop('doc')
                self.__calculate_metrics(metrics, cor_msg, doc)
                
            self.cor_cv.acquire()
        
        self.cor_cv.release()