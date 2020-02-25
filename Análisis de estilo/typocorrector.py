# -*- coding: utf-8 -*-
"""
Created on Fri Dec 20 22:09:13 2019

@author: Carlos Moreno Morera
"""

from __future__ import print_function
import os
import json
from csv import DictWriter
import conftypo as cft
import base64
from mytoken import MyToken

class TypoCorrector:
    """
    TypoCorrector class performs the task of correcting the typographic errors
    of the messages.
    
    Attributes
    ----------
    prep: list
        Shared resource wich is a list of messages with the following structure:
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
                'bodyBase64Html' : string,   # Optional
                'plainEncoding' : string,    # Optional
                'charLength' : int
                'doc' : Spacy's Doc
                'sentences' : [
                    {
                        doc: Spacy's Doc of the sentence
                        words: [Spacy's Tokens]
                    }
                ]
            }
    corrected: list
        Shared resource wich is a list of messages with the following structure:
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
    prep_cv: multiprocessing.Condition
        Conditional variable which is needed to access to the shared 
        resource (prep).
    corrected_cv: multiprocessing.Condition
        Conditional variable which is needed to access to the shared 
        resource (corrected).
    pre_fin: multiprocessing.Event
        Event which informs that the process in charge of the message 
        preprocessing has finished.
    typo_fin: multiprocessing.Event
        Event which informs that this process has finished.
    nlp: Spacy model
        Spacy's trained model which will be used for correcting typographic errors.
    oov: dict
        Dictionary where tokens out of vocabulary are stored in order to use
        them if they appears later in the correction. It has the following
        structure:
            {
            <token.text> : <MyToken class>
            }
            
    """
    
    def __init__(self, prep, corrected, prep_cv, cor_cv, prep_fin, typo_fin, nlp):
        """
        Class constructor.

        Parameters
        ----------
        prep : list
            List of preprocessed messages.
        corrected : list
            List of preprocessed messages whose typographical errors have been 
            corrected.
        prep_cv : multiprocessing.Condition
            Conditional variable for accessing to prep.
        cor_cv : multiprocessing.Condition
            Conditional variable for accessing to corrected.
        prep_fin : multiprocessing.Event
            Event which informs whether or not the preprocessing of messages has
            finished.
        typo_fin : multiprocessing.Event
            Event which informs whether or not the typographic correction of messages 
            has finished.
        nlp : spacy model
            Spacy's trained model which will be used to processed.

        Returns
        -------
        Constructed TypoCorrector class.

        """
        self.prep = prep
        self.corrected = corrected
        self.prep_cv = prep_cv
        self.corrected_cv = cor_cv
        self.pre_fin = prep_fin
        self.typo_fin = typo_fin
        self.oov = {}
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
        if os.path.exists('oov.json'):
            with open('oov.json', 'r') as fp:
                d = json.load(fp)
            for key in d:
                w = d[key]
                tok = MyToken(w['text'], w['punct'], w['rpunct'], w['lpunct'], 
                              w['url'], w['email'], w['lemma'], w['stop'], w['pos'],
                              w['bracket'])
                self.oov[key] = tok
                
    def __save_words_oov(self):
        """
        Saves the words which are considered out of vocabulary by the spacy
        model and they are correctly written.

        Returns
        -------
        None.

        """
        d = {}
        for key in self.oov:
            t = self.oov[key]
            d[key] = {'text' : t.text, 'punct': t.is_punct, 'rpunct' : t.is_right_punct,
                      'lpunct' : t.is_left_punct, 'url' : t.like_url,
                      'email' : t.like_email, 'lemma' : t.lemma_, 'stop' : t.is_stop,
                      'pos' : t.pos_, 'bracket' : t.is_bracket}
            
        with open('oov.json', 'w') as fp:
            json.dump(d, fp)
            
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
            cor = {'position' : ind, 'sentenceIndex' : s_ind, 'sentenceInit' : s_ini,
                   'token' : self.oov[msg_typo['doc'][ind].text]}
            msg_typo['corrections'].append(cor)
            return ind + 1
        else:
            ling_feat = MyToken(msg_typo['doc'][ind].text)
            
            print('You will need to introduce some linguistic features:\n')
            
            ling_feat.is_punct = self.__yes_no_question('Is the token punctuation?')
            if ling_feat.is_punct:
                ling_feat.is_left_punct = self.__yes_no_question(cft.IS_LPUNCT)
                ling_feat.is_right_punct = self.__yes_no_question(cft.IS_RPUNCT)
                ling_feat.is_bracket = self.__yes_no_question(cft.IS_BRACKET)
        
            ling_feat.like_url = self.__yes_no_question('Is it an url?')
            ling_feat.like_email = self.__yes_no_question('Is it an email?')
            
            if (self.__yes_no_question("Do you know the token's lemma?")):
                ling_feat.lemma_ = self.__req_verified_answer(cft.TOK_LEM)
                
            ling_feat.is_stop = self.__yes_no_question('Is a stop word?')
            
            if (self.__yes_no_question("Do you know the token's part-of-speech?")):
                ling_feat.pos_ = self.__req_verified_answer(cft.TOK_POS)
            
            if (self.__yes_no_question(cft.SAVE_OOV)):
                self.oov[msg_typo['doc'][ind].text] = ling_feat
            
            cor = {'position' : ind, 'sentenceIndex' : s_ind, 'sentenceInit' : s_ini,
                   'token' : ling_feat}
            msg_typo['corrections'].append(cor)
            return ind + 1
    
    def __copy_data(self, prep_msg, msg_typo):
        """
        Copies the data from the preprocessed message to the message with the
        typographic errors corrected.
        
        Parameters
        ----------
        prep_msg: dict
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
                    'bodyBase64Plain' : string,
                    'bodyBase64Html' : string,   # Optional
                    'plainEncoding' : string,    # Optional
                    'charLength' : int
                    'sentences' : [ [ string ] ]
                    ]
                }
        msg_typo: dict
            Dictionary where the data is going to be copied.
            
        Returns
        -------
        None.
        
        """
        msg_typo['id'] = prep_msg['id']
        msg_typo['threadId'] = prep_msg['threadId']
        msg_typo['to'] = prep_msg['to']
        msg_typo['cc'] = prep_msg['cc']
        msg_typo['bcc'] = prep_msg['bcc']
        msg_typo['from'] = prep_msg['from']
        msg_typo['depth'] = prep_msg['depth']
        msg_typo['date'] = prep_msg['date']
        
        if 'subject' in prep_msg:
            msg_typo['subject'] = prep_msg['subject']
        
        if 'plainEncoding' in prep_msg:
            msg_typo['plainEncoding'] = prep_msg['plainEncoding']
        
    def correct_msgs(self, user):
        """
        Obtains the preprocessed messages and corrects all the typographic errors
        on them. Besides this method saves the preprocessed messages before the 
        correction.
        
        Parameters
        ----------
        user: str
            User name of the owner of the messages.
            
        Returns
        -------
        None.
        
        """
        if not os.path.exists(user + '/Preprocessing'):
            os.mkdir(user + '/Preprocessing')
            
        if not os.path.exists(user + '/Preprocessing/preprocessed.csv'):
            csvfile = open(user + '/Preprocessing/preprocessed.csv', 'w')
            writer = DictWriter(csvfile, fieldnames = cft.CSV_COL)
            writer.writeheader()
        else:
            csvfile = open(user + '/Preprocessing/preprocessed.csv', 'a')
            writer = DictWriter(csvfile, fieldnames = cft.CSV_COL)
        
        self.prep_cv.acquire()
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
                
                msg_typo['bodyPlain'] = prep_msg['bodyPlain']
                msg_typo['doc'] = prep_msg.pop('doc')
                msg_typo['sentences'] = prep_msg['sentences'].copy()
                msg_typo['corrections'] = []
                
                discard = False
                if (msg_typo['doc'][0].pos_ != 'SPACE' and msg_typo['doc'][0].is_oov):
                    print('Typographic error found in the begining of the message.\n')
                    print('This is the text:\n\n')
                    print(msg_typo['bodyPlain'])
                    discard = self.__yes_no_question(cft.DISC_MSG)
                
                i = 0
                # Sentence index: indicates the initial token of the sentence
                s_ind = -1
                # Sentence init: indicates the position of the first chartacter
                s_ini = 0
                # Number of typo errors detected
                count = 0
                while (i < len(msg_typo['doc']) and not(discard)):
                    # If the token stars a sentence
                    if msg_typo['doc'][i].is_sent_start:
                        s_ind += 1
                        s_ini = msg_typo['doc'][i].idx
                    
                    if (msg_typo['doc'][i].pos_ != 'SPACE' and 
                        msg_typo['doc'][i].is_oov):
                        i = self.__req_token_correction(i, msg_typo, s_ind, s_ini)
                        count += 1
                        
                        if count == cft.TOO_MANY_TYPO:
                            print(f'{count} typographic errors found.')
                            discard = self.__yes_no_question(cft.DISC_MSG)
                    else:
                        i += 1
                
                if not(discard):
                    for j in range(len(prep_msg['sentences'])):
                        prep_msg['sentences'][j] = [t.text for t in 
                            prep_msg['sentences'][j]['words']]
                    
                    self.__copy_data(prep_msg, msg_typo)
                    writer.writerow(prep_msg)
                    
                    msg_typo['charLength'] = len(msg_typo['bodyPlain'])
                    msg_typo['bodyBase64Plain'] = base64.urlsafe_b64encode(
                        msg_typo['bodyPlain'].encode()).decode()
                    
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