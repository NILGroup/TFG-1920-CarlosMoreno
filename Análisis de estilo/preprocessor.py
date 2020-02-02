# -*- coding: utf-8 -*-
"""
Created on Sun Nov 17 18:27:33 2019

@author: Carlos Moreno Morera
"""

from __future__ import print_function
from email_reply_parser import EmailReplyParser
import base64
import os
from csv import DictWriter
from re import search
import confprep as cf

class Preprocessor:
    """
    Preprocessor class performs the task of preprocessing the extracted messages
    in order to being analysed then.
    
    Attributes
    ----------
    raw: list
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
            'bodyPlain' : string,        # Optional
            'bodyHtml' : string,         # Optional
            'bodyBase64Plain' : string,  # Optional
            'bodyBase64Html' : string,   # Optional
            'plainEncoding' : string,    # Optional
            'charLength' : int           # Optional
        }
    preprocessed: list
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
    cv_raw: multiprocessing.Condition
        Conditional variable which is needed to access to the shared 
        resource (raw).
    cv_msgs: multiprocessing.Condition
        Conditional variable which is needed to access to the shared 
        resource (preprocessed).
    extract_finished: multiprocessing.Event
        Event which informs that the process in charge of the message 
        extraction has finished.
    prep_finished: multiprocessing.Event
        Event which informs that this process has finished.
    nlp: Spacy model
        Spacy's trained model which will be used for preprocessing.
        
    """
    
    def __init__(self, raw_msgs, msgs, cv_raw, cv_msgs, ext_fin, prp_fin, nlp):
        """
        Class constructor.
        
        Parameters
        ----------
        raw_msgs: list
            List of extracted messages.
        msgs: list
            List of preprocessed messages which were obtained from raw_msgs.
        cv_raw: multiprocessing.Condition
            Conditional variable for accessing raw_msgs.
        cv_msgs: multiprocessing.Condition
            Conditional variable for accessing to msgs.
        ext_fin: multiprocessing.Event
            Event which informs whether or not the extraction of messages has
            finished.
        prp_fin: multiprocessing.Event
            Event which informs whether or not the preprocessing of messages has
            finished.
        nlp: spacy model
            Spacy's trained model which will be used to processed.

        Returns
        -------
        Constructed Preprocessor class.

        """
        self.raw = raw_msgs
        self.preprocessed = msgs
        self.cv_raw = cv_raw
        self.cv_msgs = cv_msgs
        self.extract_finished = ext_fin
        self.prep_finished = prp_fin
        self.nlp = nlp
        
    def __is_break_line_tag(self, html, pos):
        """
        Checks if the html tag causes a break line.
        
        Parameters
        ----------
        html: str
            HTML code.
        pos: int
            Position of the tag that we want to check.
            
        Returns
        -------
        bool: True if the tag causes a break line and false if it does not.
        
        """
        tag = ""
        while (html[pos] != ' ' and html):
            tag += html[pos]
            pos += 1
        return tag in cf.TAGS_BREAKS_LINE 
        
    def __remove_soft_breaks(self, plain, html):
        """
        Removes soft break lines of the message body by comparing its
        representation as a plain text and as html
        
        Parameters
        ----------
        plain: str
            Message body as plain text.
        html: str
            Message body represented as html.
            
        Returns
        -------
        str: Message body as plain text without soft break lines.
        """
        cleaned_text = ""
        ind = html.find('>') + 1
        
        for c in plain:
            while (c != html[ind] and not c in cf.BREAK_LINE):
                if html[ind] == '<':
                    ind = html.find('>', ind) + 1
                else:
                    ind += 1
                    
            while (c in cf.BREAK_LINE and html[ind] == '<' and 
                   not self.__is_break_line_tag(html, ind + 1)):
                ind = html.find('>', ind) + 1
                    
            if (not c in cf.BREAK_LINE):
                ind += 1
                cleaned_text += c
            elif (html[ind] == '<' and self.__is_break_line_tag(html, ind + 1)):
                cleaned_text += c
                ind = html.find('>', ind) + 1
        
    def __clean_decoded_text(self, text):
        """
        Removes soft break lines of the message body.

        Parameters
        ----------
        text: str
            Message body

        Returns
        -------
        str: Message body without soft break lines.
        """
        new_text = ""
        i = 0
        n = len(text)
        while i < n:
            if (text[i] == '\r' and (i + 1 < n) and text[i + 1] == '\n'):
                i += 2
                while((i + 1 < n) and text[i] == '\r' and text[i + 1] == '\n'):
                    new_text += text[i] + text[i + 1]
                    i += 2
            elif (text[i] == '\n'):
                i += 1
                while((i < n) and text[i] == '\n'):
                    new_text += text[i]
                    i += 1
            else:
                new_text += text[i]
                i += 1
    
        return new_text
    
    def __remove_signature(self, text, sign):
        """
        Removes the signature from the text of the email.
        
        Parameters
        ----------
        text: str
            Email body.
        sign: str
            Signature.
            
        Returns
        -------
        str: text without signature if it was found, and the original text
            in other case.
            
        """
        ind = text.rfind(sign)
        if ind + len(sign) >= len(text) - cf.CHAR_ERROR:
            return text[:ind]
        else:
            return text
        
    def __remove_header_replied(self, text):
        """
        Removes the header with which the replied text begins.
        
        Parameters
        ----------
        text: str
            Email body.
            
        Returns
        -------
        str: text without the header if it was found, and the original text in
            other case.
        """
        match = search(cf.REPLY_PATTERN, text)
        if match is not None:
            return text[:match.start()] + text[match.end():]
        else:
            return text
        
    def __extract_body_msg(self, msg_prep, msg_raw):
        """
        Extracts the body message from the raw message. For achieving this
        goal, this function removes the text of the replied email (if it
        exists) and the soft break lines inserted in the body.

        Parameters
        ----------
        msg_prep : dict
            Dictionary where the extracted text is going to be stored.
        msg_raw : dict
            Dictionary with the raw information of the message.

        Returns
        -------
        None.

        """
        if msg_raw['depth'] > 0:
            ind = msg_raw['bodyPlain'].find(cf.FOWARD_LINE)
            if (ind >= 0):
                # As we can't detect (without comparing it) which 
                # part of the message is originally text of the 
                # forwarded message, we delete all that part.
                msg_raw['bodyPlain'] = msg_raw['bodyPlain'][:ind]
            msg_prep['bodyPlain'] = EmailReplyParser.parse_reply(
                msg_raw.pop('bodyPlain'))
            msg_prep['bodyPlain'] = self.__remove_header_replied(
                msg_prep['bodyPlain'])
                
            if 'bodyHtml' in msg_raw:
                msg_prep['bodyPlain'] = self.__remove_soft_breaks(
                    msg_prep['bodyPlain'], msg_raw.pop('bodyHtml'))
            elif ('plainEncoding' in msg_raw and 
                  msg_raw['plainEncoding'] == 'quoted-printable'):
                msg_prep['bodyPlain'] = self.__clean_decoded_text(
                    msg_prep['bodyPlain'])
                    
        elif 'bodyHtml' in msg_raw:
            msg_prep['bodyPlain'] = self.__remove_soft_breaks(
                msg_raw.pop('bodyPlain'), msg_raw.pop('bodyHtml'))
        elif ('plainEncoding' in msg_raw and 
              msg_raw['plainEncoding'] == 'quoted-printable'):
            msg_prep['bodyPlain'] = self.__clean_decoded_text(
                msg_raw.pop('bodyPlain'))
        else:
            msg_prep['bodyPlain'] = msg_raw.pop('bodyPlain')
            
    def __copy_metadata(self, prep, raw):
        """
        Copies the metadata of the message from the raw to the preprocessed.
        
        Parameters
        ----------
        prep : dict
            Dictionary which represents the preprocessed message.
        raw : dict
            Dictionary which represents the raw message.

        Returns
        -------
        None.
        
        """
        prep['id'] = raw['id']
        prep['threadId'] = raw['threadId']
        prep['to'] = raw['to']
        prep['cc'] = raw['cc']
        prep['bcc'] = raw['bcc']
        prep['from'] = raw['from']
        prep['depth'] = raw['depth']
        prep['date'] = raw['date']
        if 'subject' in raw:
            prep['subject'] = raw['subject']
        if ('plainEncoding' in raw and raw['plainEncoding'] is not None):
            prep['plainEncoding'] = raw['plainEncoding']
        if ('bodyBase64Html' in raw):
            prep['bodyBase64Html'] = raw['bodyBase64Html']
            
    def __get_structured_text(self, prep):
        """
        Adds to the prep dictionary a key 'doc', whose value will correspond with
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
        prep : dict
            Dictionary of the preprocessed message.

        Returns
        -------
        None.

        """
        prep['doc'] = self.nlp(prep['bodyPlain'])
        sentences = [s.text for s in prep['doc'].sents]
        prep['sentences'] = []
        
        nums = 0
        for s in sentences:
            prep['sentences'].append({})
            prep['sentences'][nums]['doc'] = self.nlp(s)
            prep['sentences'][nums]['words'] = [t for t in 
                                                prep['sentences'][nums]['doc']]
            nums += 1
            
        
    def star_preprocessing(self, user, sign = None):
        """
        Obtains the messages extracted and preprocessed them by extracting only
        the body message (removing the sign, the replied message, ...) and 
        getting a list of sentences and different words in the text. Besides
        this method saves the raw messages before the preprocessing.
        
        Parameters
        ----------
        user: str
            User name of the owner of the messages.
        sign: str (optional)
            Sign of the person who writes the emails.
            
        Returns
        -------
        None.
        
        """
        if not os.path.exists(user + '/Extraction'):
            os.mkdir(user + '/Extraction')
        
        if not os.path.exists(user + '/Extraction/extracted.csv'):
            csvfile = open(user + '/Extraction/extracted.csv', 'w')
            writer = DictWriter(csvfile, fieldnames = cf.CSV_COL)
            writer.writeheader()
        else:
            csvfile = open(user + '/Extraction/extracted.csv', 'a')
            writer = DictWriter(csvfile, fieldnames = cf.CSV_COL)
        
        self.cv_raw.acquire()
        while (not(self.extract_finished.is_set()) or len(self.raw) > 0):
            extracted = False
            while (len(self.raw) == 0 and not(self.extract_finished.is_set())):
                self.cv_raw.wait()
            if (len(self.raw) > 0):
                msg_raw = self.raw.pop()
                extracted = True
            self.cv_raw.release()
            
            if (extracted and 'bodyPlain' in msg_raw):
                msg_prep = {}
                self.__extract_body_msg(msg_prep, msg_raw)
                
                writer.writerow(msg_raw)
                if sign is not None:
                    msg_prep['bodyPlain'] = self.__remove_signature(
                        msg_prep['bodyPlain'], sign)
                
                msg_prep['bodyBase64Plain'] = base64.urlsafe_b64encode(
                    msg_prep['bodyPlain'].encode()).decode()
                
                self.__copy_metadata(msg_prep, msg_raw)
                msg_prep['charLength'] = len(msg_prep['bodyPlain'])
                
                self.__get_structured_text(msg_prep)
                
                self.cv_msgs.acquire()
                self.preprocessed.append(msg_prep)
                self.cv_msgs.notify()
                self.cv_msgs.release()
                
            self.cv_raw.acquire()
        
        self.cv_raw.release()
        
        self.cv_msgs.acquire()
        self.prep_finished.set()
        self.cv_msgs.notify()
        self.cv_msgs.release()
        
        csvfile.close()