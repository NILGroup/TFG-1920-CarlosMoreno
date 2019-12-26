# -*- coding: utf-8 -*-
"""
Created on Fri Dec 20 22:09:13 2019

@author: Carlos Moreno Morera
"""

from __future__ import print_function
import os
import json
from csv import DictWriter

class TypoCorrector:
    
    def __init__(self, prep, corrected, prep_cv, cor_cv, prep_fin, typo_fin, nlp):
        self.prep = prep
        self.corrected = corrected
        self.prep_cv = prep_cv
        self.corrected_cv = cor_cv
        self.pre_fin = prep_fin
        self.typo_fin = typo_fin
        self.__load_words_oov()
        self.nlp = nlp
        
    def __load_words_oov(self):
        """
        Loads the words which are considered out of vocabulary by the spacy
        model and they are correctly written.

        Returns
        -------
        None.

        """
        if not os.path.exists('oov.json'):
            self.oov = {}
        else:
            with open('oov.json', 'r') as fp:
                self.oov = json.load(fp)
                
    def __save_words_oov(self):
        """
        Saves the words which are considered out of vocabulary by the spacy
        model and they are correctly written.

        Returns
        -------
        None.

        """
        with open('oov.json', 'w') as fp:
            json.dump(self.oov, fp)
            
    def __yes_no_question(self, question):
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
    
    def __req_verified_answer(self, question):
        """
        Asks the user the given question and it makes sure that the answer is
        correct.
        
        Parameters
        ----------
        question: str
            Question which is going to be asked.
        
        Returns
        -------
        str: verified answer.
        
        """
        answ = input(question)
            
        sure = f'Introduced answer is: {answ}\nIs it correct?'
        while (not self.__yes_no_question(sure)):
            answ = input(question)
            sure = f'Introduced answer is: {answ}\nIs it correct?'
        return answ
    
    def __correct_typo(self, ind, msg_typo, s_ind, s_ini):
        """
        Corrects a typographic error of the token which is in the index given
        position.
        
        Parameters
        ----------
        ind: int
            Index which indicates the position of the token which has the 
            typographic error.
        msg_typo: dict
            Dictionary where the body of the message and the spacy's doc of
            it are stored.
        s_ind: int
            Index of the sentence where the typographic error is.
        s_ini: int
            Index of the begining of the sentence in the complete text.
        
        Returns
        -------
        None.
        
        """
        chosen = False
        while not chosen:
            print('Possible solutions:\n')
            print('1.- Remove word.\n')
            print('2.- Rewrite word.\n')
            try:
                opt = int(input('Choose an option: '))
                chosen = opt in {0, 1, 2}
            except ValueError:
                print('Invalid input.\n')
        
        token = msg_typo['doc'][ind]
        sentence = msg_typo['sentences'][s_ind]
        
        begining = msg_typo['bodyPlain'][:token.idx]
        s_begining = sentence['doc'].text[:token.idx - s_ini]
        ending = msg_typo['bodyPlain'][token.idx + len(token):]
        s_ending = sentence['doc'].text[token.idx - s_ini + len(token):]
        
        if opt == 1:            
            msg_typo['bodyPlain'] = begining + ending[1:]
            sent_text = s_begining + s_ending[1:]
        else:
            new_word = self.__req_verified_answer('Introduce the correct word: ')
            
            msg_typo['bodyPlain'] = begining + new_word + ending
            sent_text = s_begining + new_word + s_ending
        
        msg_typo['doc'] = self.nlp(msg_typo['bodyPlain'])
        sentence['doc'] = self.nlp(sent_text)
        sentence['words'] = [t for t in sentence['doc']]
            
    def __req_token_correction(self, ind, msg_typo, s_ind, s_ini):
        """
        Requests a token correction when the module has found a typographic
        error (which is given).
        
        Parameters
        ----------
        ind: int
            Index which indicates the position of the token which has the 
            typographic error.
        msg_typo: dict
            Dictionary where the body of the message and the spacy's doc of
            it are stored.
        s_ind: int
            Index of the sentence where the typographic error is.
        s_ini: int
            Index of the begining of the sentence in the complete text.
        
        Returns
        -------
        int: index of the next word which has to be analysed.
        
        """
        print(f'Typographic error: {msg_typo["doc"][ind].text}\n')
        print('Body message:\n\n')
        print(msg_typo['bodyPlain'])
        
        if (self.__yes_no_question('Is it a real typographic error?')):
            self.__correct_typo(ind, msg_typo, s_ind, s_ini)
            return ind
        elif msg_typo['doc'][ind].text in self.oov:
            pos = {'position' : ind, 'sentenceIndex' : s_ind, 
                   'sentencePosition' : s_ini}
            msg_typo['corrections'].append({**pos, 
                                            **self.oov[msg_typo['doc'][ind].text]})
            return ind + 1
        else:
            ling_feat = {'text' : msg_typo['doc'][ind].text}
            
            print('You will need to introduce some linguistic features:\n')
            
            ling_feat['is_punct'] = self.__yes_no_question('Is the token punctuation?')
            if ling_feat['is_punct']:
                ling_feat['is_lpunct'] = self.__yes_no_question('Is it left punctuation?')
                ling_feat['is_rpunct'] = self.__yes_no_question('Is it right punctuation?')
        
            ling_feat['is_url'] = self.__yes_no_question('Is it an url?')
            ling_feat['is_email'] = self.__yes_no_question('Is it an email?')
            
            if (self.__yes_no_question("Do you know the token's lemma?")):
                ling_feat['lemma'] = self.__req_verified_answer(
                    "Introduce the token's lemma: ")
                
            ling_feat['is_stop'] = self.__yes_no_question('Is a stop word?')
            
            if (self.__yes_no_question("Do you know the token's part-of-speech?")):
                ling_feat['pos'] = self.__req_verified_answer(
                    "Introduce the token's pos: ")
            
            if (self.__yes_no_question('Do you want to save this information in' +
                                       ' order to know what to do in the future?')):
                self.oov[msg_typo['doc'][ind].text] = ling_feat.copy()
            
            pos = {'position' : ind, 'sentenceIndex' : s_ind, 
                   'sentencePosition' : s_ini}
            msg_typo['corrections'].append({**pos, **ling_feat})
            return ind + 1
            
        
    def correct_msgs(self, user):
        if not os.path.exists(user + '/Preprocessing'):
            os.mkdir(user + '/Preprocessing')
        
        csv_columns = ['id', 'threadId', 'to', 'cc', 'bcc', 'from',
                       'depth', 'date', 'subject', 'bodyBase64Plain', 
                       'bodyBase64Html', 'plainEncoding', 'charLength']
        if not os.path.exists(user + '/Preprocessing/preprocessed.csv'):
            csvfile = open(user + '/Preprocessing/preprocessed.csv', 'w')
            writer = DictWriter(csvfile, fieldnames = csv_columns)
            writer.writeheader()
        else:
            csvfile = open(user + '/Preprocessing/preprocessed.csv', 'a')
            writer = DictWriter(csvfile, fieldnames = csv_columns)
        
        self.prep_cv.aquire()
        while (not(self.pre_fin.is_set()) or len(self.prep) > 0):
            extracted = False
            while (len(self.prep) == 0 and not(self.pre_fin.is_set())):
                self.prep_cv.wait()
            if (len(self.prep) > 0):
                prep_msg = self.prep.pop()
                extracted = True
            self.prep_cv.release()
            
            # If the body is not an empty string
            if (extracted and prep_msg['bodyPlain']):
                msg_typo = {}
                
                msg_typo['bodyPlain'] = prep_msg.pop('bodyPlain')
                msg_typo['doc'] = prep_msg.pop('doc')
                msg_typo['sentences'] = prep_msg['sentences'].copy()
                msg_typo['corrections'] = []
                
                i = 0
                s_ind = -1
                s_ini = 0   #Posibilidad de descartar email
                while i < len(msg_typo['doc']):
                    if msg_typo['doc'][i].is_sent_start:
                        s_ind += 1
                        s_ini = msg_typo['doc'][i].idx
                    
                    if msg_typo['doc'][i].is_oov:
                        i = self.__req_token_correction(i, msg_typo, s_ind, s_ini)
                    else:
                        i += 1
                                
                self.corrected_cv.acquire()
                self.corrected.append(msg_typo)
                self.corrected_cv.notify()
                self.corrected_cv.release()
                
                self.prep_cv.acquire()
        
        self.prep_cv.release()
        
        self.corrected_cv.acquire()
        self.typo_fin.set()
        self.corrected_cv.notify()
        self.corrected_cv.release()
        
        csvfile.close()
        self.__save_words_oov()