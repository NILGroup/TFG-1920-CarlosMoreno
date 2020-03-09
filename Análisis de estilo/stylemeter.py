# -*- coding: utf-8 -*-
"""
Created on Thu Jan 23 16:17:23 2020

@author: Carlos Moreno Morera
"""

from __future__ import print_function
import os
from csv import DictWriter
import confstyle as cfs
import math
import base64

class StyleMeter:
    """
    StyleMeter class performs the task of calculating some metrics which describes
    the writting style of the message.
    
    Attributes
    ----------
    corrected : list
        List of preprocessed messages whose typographical errors have been 
        corrected. Shared resource wich is a list of messages with the following 
        structure:
            {
                'id' : string,
                'threadId' : string,
                'to' : [ string ],
                'cc' : [ string ],
                'bcc' : [ string ],
                'from' : string,
                'depth' : int,               # How many messages precede it
                'date' : long,               # Epoch ms
                'subject' : string,          # Optional
                'bodyPlain' : string,
                'bodyBase64Plain' : string,
                'plainEncoding' : string,    # Optional
                'charLength' : int
                'doc' : Spacy's Doc
                'sentences' : [
                    {
                        doc: Spacy's Doc of the sentence
                        words: [Spacy's Tokens]
                    }
                ]
                'corrections' : [
                    {
                        'token' : <MyToken class>
                        'position' : int
                        'sentenceIndex' : int
                        'sentenceInit' : int
                    }
                ]
            }
    cor_cv: multiprocessing.Condition
        Conditional variable which is needed to access to the shared 
        resource (corrected).
    pre_fin: multiprocessing.Event
        Event which informs that the process in charge of the message 
        typographical correcting has finished.
        
    """
    
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
        
        metrics['wordLength'] = {1:0, 2:0}
        metrics['charLength'] = 0
        metrics['numWords'] = 0
        
        met_sents = metrics.copy()
        
        metrics['sentLength'] = {}
        metrics['sentNumWords'] = {}
        # Creates a dictionary of information for each sentence
        metrics['metricsSentences'] = [met_sents.copy() for i in range(numSentences)]
        
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
        if not(len(t.text) in m_sent['wordLength']):
            m_sent['wordLength'][len(t.text)] = 0
                    
        metrics['wordLength'][len(t.text)] += 1
        m_sent['wordLength'][len(t.text)] += 1
        if t.lemma_:
            words[t.lemma_] += 1
        metrics['numWords'] += 1
        m_sent['numWords'] += 1
                    
        if t.is_stop:
            metrics['numStopWords'] += 1
            m_sent['numStopWords'] += 1
        if t.pos_ in cfs.POS:
            metrics[t.pos_] += 1
            m_sent[t.pos_] += 1
            
    def __mean_word_length(self, metrics):
        """
        Obtains the mean word length.
        
        Parameters
        ----------
        metrics: dict
            Dictionary where the metrics are stored.
            
        Returns
        -------
        float: mean word length.
        
        """
        w_len = metrics['wordLength']
        total_char = 0
        for key in w_len:
            total_char += key * w_len[key]
        
        return total_char/metrics['numWords']
            
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
        m_sent['charLength'] = len(s['doc'].text)
            
        if not(m_sent['numWords'] in metrics['sentNumWords']):
            metrics['sentNumWords'][m_sent['numWords']] = 0
        if not(m_sent['charLength'] in metrics['sentLength']):
            metrics['sentLength'][m_sent['charLength']] = 0
                
        metrics['sentNumWords'][m_sent['numWords']] += 1
        metrics['sentLength'][m_sent['charLength']] += 1
        
        # Ril, Y., Y.C. & Fonseca, E. (2014) Determination of writing styles
        m_sent['stopRatio'] = (m_sent['numStopWords']/m_sent['numWords']) * 100
        m_sent['meanWordLen'] = self.__mean_word_length(m_sent)
        
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
        
    def __Yule_richness(self, M, words, words_appearance):
        """
        Calculates the Yule's richness of vocabulary index which could be found
        in Yule, G. U. (1944) The statistical study of literary vocabulary. Journal
        of the Royal Statistical Society, 107(2), 129-131.
        
        Parameters
        ----------
        words: dict
            Dictionary which relates each words with the number of times that
            it appears in the text.
        M: int
            Number of diferent words in the text.
        words_appearance: dict
            Dictionary which counts how many words are that they have appeared
            the key number of times.
            
        Returns
        -------
        float: Yule's richness of vocabulary index.
        
        """
        for key in words:
            if not(words[key] in words_appearance):
                words_appearance[words[key]] = 0
            words_appearance[words[key]] += 1
            
        yule_sum = 0
        for i in words_appearance:
            yule_sum += (math.pow(i, 2) * words_appearance[i] - M)
            
        return (math.pow(10, 4) * yule_sum) / math.pow(M, 2)
    
    def __Simpson_Index(self, M, YuleChar):
        """
        Obtains the Simpson's Index from the Yule's Characteristic or Yule's 
        richness of vocabulary index. The Simpson's index could be found in
        Simpson, E.H. (1949). Measurement of diversity. Nature, 163, 688.
        
        Parameters
        ----------
        M: int
            Number of diferent words in the text.
        YuleChar: float
            Yule's richness of vocabulary index.
            
        Returns
        -------
        float: Simpson's Index.
        
        """
        return YuleChar/(math.pow(10, 4)*(1-1/M))
    
    def __entropy(self, words, numWords):
        """
        Calculates the entropy of the given text.

        Parameters
        ----------
        words : dict
            Dictionary which relates each words with the number of times that
            it appears in the text.
        numWords : int
            Number of words in the text.

        Returns
        -------
        float: entropy.

        """
        H = 0
        for key in words:
            p = words[key]/numWords
            H += p * math.log(p)/math.log(numWords)
        return -100 * H
    
    def __calculate_metrics(self, metrics, cor_msg, doc):
        """
        Calculates the style metrics.
        
        Parameters
        ----------
        metrics : dict
            Dictionary where the metrics are going to be stored.
        cor_msg: dict
            Dictionary which stores the information of the message whose
            typographic errors has been corrected.
        doc: Spacy's doc
        
        Returns
        -------
        None.
        
        """
        self.__initialize_metrics(metrics, len(cor_msg['sentences']))
        
        words = {}
        open_brackets = 0
        ind_sent = 0
        ind_cor = 0
        
        for s in cor_msg['sentences']:
            m_sent = metrics['metricsSentences'][ind_sent]
            for t in s['words']:
                if t.pos_ != 'SPACE' and t.is_oov:
                    cor = cor_msg['corrections'][ind_cor]
                    t = cor['token']
                    ind_cor += 1
                    
                if t.is_punct:
                    open_brackets = self.__calculate_punct_metrics(metrics, m_sent, 
                                                                   open_brackets, t)
                elif not(t.like_url or t.like_email):
                    self.__calculate_word_metrics(metrics, m_sent, words, t)
            
            self.__calculate_sentence_metrics(metrics, m_sent, s)
            ind_sent += 1
        
        metrics['charLength'] = cor_msg['charLength']
        
        # Ril, Y., Y.C. & Fonseca, E. (2014) Determination of writing styles
        metrics['stopRatio'] = (metrics['numStopWords']/metrics['numWords']) * 100
        # Flesch-Kincaid (DuBay, 2004)
        metrics['difficultyLevel'] = self.__Flesch_Kincaid_Index(metrics)
        # Honoré, A. (1979). Some simple measures of richness of vocabulary.
        M = len(words)
        metrics['richnessVocab'] = (100 * math.log(M))/(math.pow(M, 2))
        metrics['wordsAppearance'] = {}
        # Yule, G. U. (1944) The statistical study of literary vocabulary.
        metrics['richnessYule'] = self.__Yule_richness(M, words, 
                                                       metrics['wordsAppearance'])
        metrics['meanSentLen'] = metrics['numWords']/len(cor_msg['sentences'])
        metrics['meanWordLen'] = self.__mean_word_length(metrics)
        metrics['numDifWords'] = len(words)
        
        if metrics['ADJ'] != 0:
            metrics['verbAdjectiveRatio'] = metrics['VERB']/metrics['ADJ']
        if metrics['PRON'] != 0:
            metrics['detPronRatio'] = metrics['DET']/metrics['PRON']
        
        # Simpson, E.H. (1949). Measurement of diversity
        metrics['SimpsonIndex'] = self.__Simpson_Index(M, metrics['richnessYule'])
        metrics['entropy'] = self.__entropy(words, metrics['numWords'])
        
    def __create_typo_writer(self, user):
        """
        Creates a csv dictionary writer for the messages that have been typographical
        corrected.
        
        Parameters
        ----------
        user: str
            Gmail user.
        
        Returns
        -------
        DictWriter: csv dictionary writer.
        File descriptor: csv file descriptor.
        
        """
        if not os.path.exists(user + '/TypoCorrection'):
            os.mkdir(user + '/TypoCorrection')
            
        if not os.path.exists(user + '/TypoCorrection/typocorrected.csv'):
            csvtypo = open(user + '/TypoCorrection/typocorrected.csv', 'w')
            writerTypo = DictWriter(csvtypo, fieldnames = cfs.CSV_TYPO_COL)
            writerTypo.writeheader()
        else:
            csvtypo = open(user + '/TypoCorrection/typocorrected.csv', 'a')
            writerTypo = DictWriter(csvtypo, fieldnames = cfs.CSV_TYPO_COL)
        return writerTypo, csvtypo
    
    def __create_metrics_writer(self, user):
        """
        Creates a csv dictionary writer for the calculated metrics.
        
        Parameters
        ----------
        user: str
            Gmail user.
        
        Returns
        -------
        DictWriter: csv dictionary writer.
        File descriptor: csv file descriptor.
        
        """
        if not os.path.exists(user + '/Metrics'):
            os.mkdir(user + '/Metrics')
                
        if not os.path.exists(user + '/Metrics/stylemetrics.csv'):
            csvMetrics = open(user + '/Metrics/stylemetrics.csv', 'w')
            writerMetrics = DictWriter(csvMetrics, fieldnames = cfs.CSV_MET_COL)
            writerMetrics.writeheader()
        else:
            csvMetrics = open(user + '/Metrics/stylemetrics.csv', 'a')
            writerMetrics = DictWriter(csvMetrics, fieldnames = cfs.CSV_MET_COL)
        return writerMetrics, csvMetrics
        
    def __copy_metadata(self, metrics, cor_msg):
        """
        Copies the data from the corrected message to the dictionary that
        stores the metrics.
        
        Parameters
        ----------
        metrics: dict
            Dictionary where the data is going to be copied.
        cor_msg: dict
            Dictionary which represents the preprocessed message. It has the
            next structure:
                {
                'id' : string,
                'threadId' : string,
                'to' : [ string ],
                'cc' : [ string ],
                'bcc' : [ string ],
                'from' : string,
                'depth' : int,               # How many messages precede it
                'date' : long,               # Epoch ms
                'subject' : string,          # Optional
                'bodyPlain' : string,
                'bodyBase64Plain' : string,
                'plainEncoding' : string,    # Optional
                'charLength' : int
                'doc' : Spacy's Doc
                'sentences' : [
                    {
                        doc: Spacy's Doc of the sentence
                        words: [Spacy's Tokens]
                    }
                ]
                'corrections' : [
                    {
                        'token' : <MyToken class>
                        'position' : int
                        'sentenceIndex' : int
                        'sentenceInit' : int
                    }
                ]
            }
            
        Returns
        -------
        None.
        
        """
        metrics['id'] = cor_msg['id']
        metrics['threadId'] = cor_msg['threadId']
        metrics['to'] = cor_msg['to']
        metrics['cc'] = cor_msg['cc']
        metrics['bcc'] = cor_msg['bcc']
        metrics['from'] = cor_msg['from']
        metrics['depth'] = cor_msg['depth']
        metrics['date'] = cor_msg['date']
        
        if 'subject' in cor_msg:
            metrics['subject'] = cor_msg['subject']
    
    def measure_style(self, user):
        """
        Measures the writting style of the messages of the given user.

        Parameters
        ----------
        user : str
            Gmail user.

        Returns
        -------
        None.

        """
        writerTypo, csvtypo = self.__create_typo_writer(user)
        writerMetrics, csvMetrics = self.__create_metrics_writer(user)
            
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
                self.__copy_metadata(metrics, cor_msg)
                
                for j in range(len(cor_msg['sentences'])):
                    cor_msg['sentences'][j] = [base64.urlsafe_b64encode(
                        t.text.encode()).decode() for t in 
                        cor_msg['sentences'][j]['words']]
                    
                for j in range(len(cor_msg['corrections'])):
                    cor_msg['corrections'][j] = base64.urlsafe_b64encode(
                        cor_msg['corrections'][j]['token'].text.encode()).decode()
                
            writerTypo.writerow(cor_msg)
            writerMetrics.writerow(metrics)
            self.cor_cv.acquire()
            
        self.cor_cv.release()
        csvtypo.close()
        csvMetrics.close()