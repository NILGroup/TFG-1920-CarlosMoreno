# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 14:32:54 2019

@author: Carlos Moreno Morera
"""
from __future__ import print_function
import quotaunits as qu
from extraction.messageextractor import MessageExtractor
from extraction.threadextractor import ThreadExtractor
import confanalyser as cfa
import requests
from extraction.extractedmessage import ExtractedMessage
import json
from initdb import init_db
from preprocess.preprocessedmessage import PreprocessedMessage
from typocorrection.typocode import TypoCode
from typocorrection.correctedmessage import CorrectedMessage

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

class Analyser:
    """
    The class Analyser performs the task of analysing all the messages of a
    user in order to obtain metrics which differentiate between the style
    writing of each person.
    
    Attributes
    ----------
    service: Gmail resource
        Gmail API resource with an Gmail user session opened.
    user_name: str
        Gmail user name.
    quota: int
        Gmail API quota units available for message extraction. Represents the
        remaining quota units available to carry out the extraction operations.
    extractor: Extractor
        Object which performs the task of extracting sent messages 
        or sent threads from the user by accessing Gmail API.
    typocorrector: TypoCorrector
        Object which performs the task of correcting typographic errors from
        preprocessed messages in order to being analysed then.
    nres: int
        Number of the resource that is going to be extracted (messages or threads).
            
    """
    def __init__(self, service, usu, quota = qu.QUOTA_UNITS_PER_DAY, ext_msg = None,
                 num_extracted = None):
        """
        Class constructor.

        Parameters
        ----------
        service : Gmail resource
            Gmail API resource with an Gmail user session opened.
        usu: str
            Gmail user name.
        quota : int, optional
            Gmail API quota units available for message extraction. The default 
            is qu.QUOTA_UNITS_PER_DAY.
        ext_msg: bool, optional
            Indicates whether there were a previous extraction and whether it
            extracts messages or threads. The default is None.
        num_extracted: int, optional
            If it was an extraction before, it indicates the number of resources
            extracted last time. The default is None.

        Returns
        -------
        Constructed Analyser class.

        """
        self.service = service
        self.user_name = usu
        self.quota = quota
        
        if (self.quota > qu.LABELS_GET):
            self.extractor = None
            
            l = self.service.users().labels()
            sent_lb = l.get(userId = 'me', id = 'SENT').execute()
            self.nres = sent_lb['messagesTotal']
            self.quota -= qu.LABELS_GET

            cost_msg_ext = self.__get_res_cost(qu.MSG_LIST, sent_lb['messagesTotal'], 
                                               qu.MSG_GET)
            cost_thrd_ext = self.__get_res_cost(qu.THREADS_LIST, sent_lb['threadsTotal'], 
                                                qu.THREADS_GET)

            if (((ext_msg is None) and cost_msg_ext <= cost_thrd_ext) or ext_msg):
                with open('log.txt', 'a') as f:
                    f.write('Message extractor has been selected.\n')
                self.extractor = MessageExtractor(self.service, self.user_name, 
                                                  self.quota)
            else:
                with open('log.txt', 'a') as f:
                    f.write('Thread extractor has been selected.\n')
                self.extractor = ThreadExtractor(self.service, self.user_name,
                                                 self.quota)
                self.nres = sent_lb['threadsTotal']
                
            if ext_msg is not None:
                self.nres -= num_extracted

    def __get_res_cost(self, listcost, numres, getcost):
        """
        Gets the cost of extracting a resource (message or thread).
        
        Parameters
        ----------
        listcost: int
            Cost of getting a list of the resource in quota units.
        numres: int
            Number of the resource that is going to be extracted.
        getcost: int
            Cost of getting a resource in quota units.
            
        Returns
        -------
        int: cost of extracting the resource.
        
        """
        return listcost * (numres // cfa.NUM_RESOURCE_PER_LIST + 1) + getcost * numres
    
    def __preprocess_message(self, ide, sign, prep_ids):
        """
        Preprocess the extracted message which has the given identifier.

        Parameters
        ----------
        ide : str
            Identifier of the extracted message which is going to be
            preprocessed.
        sign : str
            Signature of the user in his emails.
        prep_ids : list
            List of the identifiers of the messages which have been
            preprocessed.

        Returns
        -------
        None.

        """
        ext_msg = ExtractedMessage.objects(msg_id = ide).first().to_json()
        ext_msg = json.loads(ext_msg)
        response = requests.post(cfa.URL_PREP, json = {'message' : ext_msg,
                                              'sign': sign})
        if response.status_code != 200:
            with open('logerror.txt', 'a') as f:
                f.write(f"Preprocess error of {ext_msg['_id']}.\n")
        else:
            response_dic = json.loads(response.content)
            if response_dic['id'] is not None:
                prep_ids.append(response_dic['id'])
                
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
        while (not yes_no_question(sure)):
            answ = input(question)
            sure = f'Introduced answer is: {answ}\nIs it correct?'
        return answ
                
    def __correct_typo(self, ind, msg_typo, typoError, token_idx):
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
        typoError: str
            Text of the token which has the typographic error.
        token_idx: int
            Integer which indicates the position of the first character of the
            token recognised as a typographic error.
        
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

        begining = msg_typo['bodyPlain'][:token_idx]
        ending = msg_typo['bodyPlain'][token_idx + len(typoError):]

        if opt == 1:            
            msg_typo['bodyPlain'] = begining + ending[1:]
        else:
            new_word = self.__req_verified_answer('Introduce the correct word: ')
            msg_typo['bodyPlain'] = begining + new_word + ending
                
    def __req_token_correction(self, ind, msg_typo, typoError, token_idx):
        """
        Requests a token correction when the module has found a typographic
        error (which is given).
        
        Parameters
        ----------
        ind: int
            Index which indicates the position of the token which has the 
            typographic error.
        msg_typo: dict
            Dictionary where the body of the message is stored.
        typoError: str
            Text of the token which has the typographic error.
        token_idx: int
            Integer which indicates the position of the first character of the
            token recognised as a typographic error.
        
        Returns
        -------
        int: index of the next word which has to be analysed.
        
        """
        print(f'Typographic error: {typoError}\n')
        print('Body message:\n\n')
        print(msg_typo['bodyPlain'])

        if (yes_no_question('Is it a real typographic error?')):
            self.__correct_typo(ind, msg_typo, typoError, token_idx)
            return ind
        else:
            ling_feat = {'text' : typoError}

            print('You will need to introduce some linguistic features:\n')
            
            if yes_no_question('Is it a NOUN'):
                ling_feat['is_punct'] = False
                ling_feat['like_url'] = False
                ling_feat['like_email'] = False
                ling_feat['pos_'] = 'NOUN'
            else:
                ling_feat['is_punct'] = yes_no_question('Is the token punctuation?')
                if ling_feat['is_punct']:
                    ling_feat['is_left_punct'] = yes_no_question(cfa.IS_LPUNCT)
                    ling_feat['is_right_punct'] = yes_no_question(cfa.IS_RPUNCT)
                    ling_feat['is_bracket'] = yes_no_question(cfa.IS_BRACKET)
    
                ling_feat['like_url'] = yes_no_question('Is it an url?')
                ling_feat['like_email'] = yes_no_question('Is it an email?')
                
                if (yes_no_question("Do you know the token's part-of-speech?")):
                    ling_feat['pos_'] = self.__req_verified_answer(cfa.TOK_POS)

            if (yes_no_question("Do you know the token's lemma?")):
                ling_feat['lemma_'] = self.__req_verified_answer(cfa.TOK_LEM)

            ling_feat['is_stop'] = yes_no_question('Is a stop word?')

            if (yes_no_question(cfa.SAVE_OOV)):
                response = requests.post(cfa.URL_TYPO_SAVE, json = ling_feat)
                if response.status_code != 200:
                    with open('logerror.txt', 'a') as f:
                        f.write(f"Save-oov error with {ling_feat['text']}.\n")
            
            ling_feat['position'] = ind
            msg_typo['corrections'].append(ling_feat)
            return ind + 1
                
    def __correct_message(self, ide, cor_ids):
        """
        Corrects the typographic errors of the preprocessed message which has
        the given identifier.
        
        Parameters
        ----------
        ide : str
            Identifier of the preprocessed message which is going to be
            corrected.
        cor_ids : list
            List of the identifiers of the messages which have been
            corrected.

        Returns
        -------
        None.
        
        """
        prep_msg = PreprocessedMessage.objects(msg_id = ide).first().to_json()
        prep_msg = json.loads(prep_msg)
        response = requests.post(cfa.URL_TYPO_CORRECT, json = {
                                                    'message' : prep_msg,
                                                    'index' : 0})
        if response.status_code != 200:
            with open('logerror.txt', 'a') as f:
                f.write(f"Typo-correction error of {prep_msg['_id']}.\n")
        else:
            resp_dic = json.loads(response.content)
            
            discard = False
            if resp_dic['typoCode'] == TypoCode.typoFound.name:
                print(f"Typographic error found in {ide}.")
                print('This is the text:\n\n')
                print(resp_dic['message']['bodyPlain'])
                discard = yes_no_question(cfa.DISC_MSG)
                
            if not(discard):
                while (response.status_code == 200 and 
                       resp_dic['typoCode'] == TypoCode.typoFound.name):
                    prep_msg = resp_dic['message']
                    ind = self.__req_token_correction(resp_dic['index'], 
                                                      prep_msg, resp_dic['typoError'],
                                                      resp_dic['token_idx'])
                    response = requests.post(cfa.URL_TYPO_CORRECT, json = {
                                                        'message' : prep_msg,
                                                        'index' : ind})
                    if response.status_code == 200:
                        resp_dic = json.loads(response.content)
                
                if response.status_code != 200:
                    with open('logerror.txt', 'a') as f:
                        f.write(f"Typo-correction error of {prep_msg['id']}.\n")
                elif resp_dic['typoCode'] == TypoCode.successful.name:
                        cor_ids.append(resp_dic['message']['id'])
                        
    def __measure_style(self, ide):
        """
        Measures the writting style of the message with the given identifier.

        Parameters
        ----------
        ide : str
            Identifier of the message which is going to be analysed.

        Returns
        -------
        None.

        """
        cor_msg = CorrectedMessage.objects(msg_id = ide).first().to_json()
        cor_msg = json.loads(cor_msg)
        response = requests.post(cfa.URL_MET, json = {'message' : cor_msg})
        
        if response.status_code != 200:
            with open('logerror.txt', 'a') as f:
                f.write(f"Metrics error with {cor_msg['_id']}.\n")
                
        else:
            response_dic = json.loads(response.content)
            if response_dic['id'] is not None:
                with open(self.user_name + '.txt', 'a') as f:
                    f.write(f"{response_dic['id']}\n")
    
    def analyse(self, nextPageToken = None, sign = None):
        """
        Analyses all the messages of the given user.
        
        Parameters
        ----------
        nextPageToken: str, optional
            Token of the next page for extracting messages. The default is None.
        sign: str, optional
            Signature of the user in his emails. The default value is None.
            
        Returns
        -------
        None.
        
        """
        init_db()
        self.quota, ext_ids = self.extractor.extract_sent_msg(self.nres, nextPageToken)
        prep_ids = []
        cor_ids = []
        for ide in ext_ids:
            self.__preprocess_message(ide, sign, prep_ids)
                
        for ide in prep_ids:
            self.__correct_message(ide, cor_ids)
            
        for ide in cor_ids:
            self.__measure_style(ide)
        
        with open('log.txt', 'a') as f:
            f.write('\nANALYSIS FINISHED:\n')
            f.write(f'{len(ext_ids)} messages have been preprocessed.\n')
            f.write(f'{len(prep_ids)} messages have been typo-corrected.\n')
            f.write(f'{len(cor_ids)} messages have been measured.\n')
        