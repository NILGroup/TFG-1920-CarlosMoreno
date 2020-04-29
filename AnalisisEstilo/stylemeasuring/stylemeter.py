# -*- coding: utf-8 -*-
"""
Created on Thu Jan 23 16:17:23 2020

@author: Carlos Moreno Morera
"""

from __future__ import print_function
import stylemeasuring.confstyle as cfs
import math
import base64
from stylemeasuring.metrics import Metrics

class StyleMeter:
    """
    StyleMeter class performs the task of calculating some metrics which describes
    the writting style of the message.
        
    Attributes
    ----------
    nlp: Spacy model
        Spacy's trained model which will be used for calculating all the style
        metrics.
        
    """
    
    def __init__(self, nlp):
        """
        Class constructor.
        
        Parameters
        ----------
        nlp: Spacy model
            Spacy's trained model which will be used for calculating all the
            style metrics.
        Returns
        -------
        Constructed StyleMeter class.
        
        """
        self.nlp = nlp
        
    def __get_structured_text(self, msg):
        """
        Adds to the msg dictionary a key 'doc', whose value will correspond with
        the Spacy's Doc of the body of the message, and a key 'sentences', whose
        value will have the next structure:
            [
                {
                    doc: Spacy's Doc of the sentence
                    words: [Spacy's Tokens]
                }
            ]
        Parameters
        ----------
        msg : dict
            Dictionary of the corrected message.
        Returns
        -------
        None.
        
        """
        msg['doc'] = self.nlp(msg['bodyPlain'])
        sentences = [s.text for s in msg['doc'].sents]
        msg['sentences'] = []

        for s in sentences:
            msg['sentences'].append({})
            msg['sentences'][-1]['doc'] = self.nlp(s)
            msg['sentences'][-1]['words'] = [t for t in 
                                                msg['sentences'][-1]['doc']]
        
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
        
        metrics['wordLength'] = {'1':0, '2':0}
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
        t: Spacy's Token
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
                    
        if not(str(len(t.text)) in metrics['wordLength']):
            metrics['wordLength'][str(len(t.text))] = 0
        if not(str(len(t.text)) in m_sent['wordLength']):
            m_sent['wordLength'][str(len(t.text))] = 0
                    
        metrics['wordLength'][str(len(t.text))] += 1
        m_sent['wordLength'][str(len(t.text))] += 1
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
            total_char += int(key) * w_len[key]
        
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
            
        if not(str(m_sent['numWords']) in metrics['sentNumWords']):
            metrics['sentNumWords'][str(m_sent['numWords'])] = 0
        if not(str(m_sent['charLength']) in metrics['sentLength']):
            metrics['sentLength'][str(m_sent['charLength'])] = 0
                
        metrics['sentNumWords'][str(m_sent['numWords'])] += 1
        metrics['sentLength'][str(m_sent['charLength'])] += 1
        
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
        one_syllable = metrics['wordLength']['1'] + metrics['wordLength']['2']
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
            beta += int(key) * metrics['sentNumWords'][key]
        
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
            if not(str(words[key]) in words_appearance):
                words_appearance[str(words[key])] = 0
            words_appearance[str(words[key])] += 1
            
        yule_sum = 0
        for i in words_appearance:
            yule_sum += (math.pow(int(i), 2) * words_appearance[i] - M)
            
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
                    t = cfs.MyToken(**cor)
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
        
    def __copy_metadata(self, metrics, cor_msg):
        """
        Copies the data from the corrected message to the dictionary that
        stores the metrics.
        
        Parameters
        ----------
        metrics: dict
            Dictionary where the data is going to be copied.
        cor_msg: dict
            Dictionary which represents the corrected message. It has the
            next structure:
                {
                'id' : string,
                'threadId' : string,
                'to' : [ string ],
                'cc' : [ string ],
                'bcc' : [ string ],
                'sender' : string,
                'depth' : int,               # How many messages precede it
                'date' : long,               # Epoch ms
                'subject' : string,          # Optional
                'bodyPlain' : string,
                'bodyBase64Plain' : string,
                'plainEncoding' : string,    # Optional
                'charLength' : int,
                'doc' : Spacy's Doc,
                'sentences' : [
                    {
                        doc: Spacy's Doc of the sentence
                        words: [Spacy's Tokens]
                    }
                ],
                'corrections' : [
                    {
                        'text': str,
                        'is_punct': bool,
                        'is_right_punct': bool,
                        'is_left_punct': bool,
                        'like_url': bool,
                        'like_email': bool,
                        'lemma_': str,
                        'is_stop': bool,
                        'pos_': str,
                        'is_bracket': bool,
                        'position': int
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
        metrics['sender'] = cor_msg['sender']
        metrics['depth'] = cor_msg['depth']
        metrics['date'] = cor_msg['date']
        
        if 'subject' in cor_msg:
            metrics['subject'] = cor_msg['subject']
    
    def measure_style(self, cor_msg):
        """
        Measures the writting style of the given message.

        Parameters
        ----------
        cor_msg : dict
            Dictionary which represents the corrected message. It has the
            next structure:
                {
                'id' : string,
                'threadId' : string,
                'to' : [ string ],
                'cc' : [ string ],
                'bcc' : [ string ],
                'sender' : string,
                'depth' : int,               # How many messages precede it
                'date' : long,               # Epoch ms
                'subject' : string,          # Optional
                'bodyBase64Plain' : string,
                'plainEncoding' : string,    # Optional
                'charLength' : int,
                'corrections' : [
                    {
                        'text': str,
                        'is_punct': bool,
                        'is_right_punct': bool,
                        'is_left_punct': bool,
                        'like_url': bool,
                        'like_email': bool,
                        'lemma_': str,
                        'is_stop': bool,
                        'pos_': str,
                        'is_bracket': bool,
                        'position': int
                    }
                ]
            }

        Returns
        -------
        None.

        """
        metrics = {}
        if not('bodyPlain' in cor_msg):
            cor_msg['bodyPlain'] = base64.urlsafe_b64decode(
                        cor_msg['bodyBase64Plain'].encode()).decode()
        self.__get_structured_text(cor_msg)
        doc = cor_msg.pop('doc')
        self.__calculate_metrics(metrics, cor_msg, doc)
        self.__copy_metadata(metrics, cor_msg)
        met = Metrics(**metrics)
        met.save()
                