# -*- coding: utf-8 -*-
"""
Created on Sun Nov 17 18:27:33 2019

@author: Carlos Moreno Morera
"""

from __future__ import print_function
from email_reply_parser import EmailReplyParser
import base64
from re import search
import preprocess.confprep as cf
from preprocess.preprocessedmessage import PreprocessedMessage

class Preprocessor:
    """
    Preprocessor class performs the task of preprocessing the extracted messages
    in order to being analysed then.
        
    """
        
    def __extract_html_tag(self, html, pos):
        """
        Extracts the HTML tag in the given position of the given string.

        Parameters
        ----------
        html: str
            HTML code.
        pos: int
            Position of the tag that we want to check.

        Returns
        -------
        str: HTML tag.

        """
        tag = ""
        while (html[pos] != ' ' and html[pos] != '>'):
            tag += html[pos]
            pos += 1
        return tag
        
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
        return self.__extract_html_tag(html, pos) in cf.TAGS_BREAKS_LINE
    
    def __is_text_format_tag(self, html, pos):
        """
        Checks if the html tag modifies the text's format.
        
        Parameters
        ----------
        html: str
            HTML code.
        pos: int
            Position of the tag that we want to check.
            
        Returns
        -------
        bool: True if the tag modifies the text's format and false if it does
        not.
        
        """
        return self.__extract_html_tag(html, pos) in cf.TAGS_FORMAT_TEXT
        
    def __is_known_tag(self, html, pos):
        """
        Checks if the html tag is a list tag, a break line tag or a text format
        tag.
        
        Parameters
        ----------
        html: str
            HTML code.
        pos: int
            Position of the tag that we want to check.
            
        Returns
        -------
        bool: True if the tag is a list tag, a break line tag or a text format
        tag and false if it does not.
        
        """
        tag = self.__extract_html_tag(html, pos)
        return ((tag in cf.TAGS_BREAKS_LINE) or (tag in cf.TAGS_FORMAT_TEXT) or
            (tag in cf.TAGS_LIST))
    
    def __is_vspace_tag(self, html, pos):
        """
        Checks if the html tag is a list tag or a break line tag.
        
        Parameters
        ----------
        html: str
            HTML code.
        pos: int
            Position of the tag that we want to check.
            
        Returns
        -------
        bool: True if the tag is a list tag or a break line tag and false if 
        it does not.
        
        """
        tag = self.__extract_html_tag(html, pos)
        return ((tag in cf.TAGS_BREAKS_LINE) or (tag in cf.TAGS_LIST))
    
    def __carriage_return_followed_by_newline(self, pos, plain):
        """
        Checks if the character of is a carriage return character followed 
        by a newline character.
        
        Parameters
        ----------
        pos: int
            Position of the character that we want to check.
        plain: str
            Message body as plain text.
            
        Returns
        -------
        bool: True if it is a carriage return character followed by a newline
        character and False otherwise.
        
        """
        return (plain[pos] == '\r' and pos < len(plain) - 1 and 
                plain[pos + 1] == '\n')
    
    def __find_first_known_tag(self, c, html, ind):
        """
        Finds the first known tag.
        
        Parameters
        ----------
        c : str
            Character of the plain text.
        html : str
            Message body represented as html.
        ind : int
            Position from which we will look for a known label.
            
        Returns
        -------
        ind : int
            Position where the known label is.
        
        """
        while (html[ind] == '<' and not self.__is_known_tag(html, ind + 1)):
            ind = html.find('>', ind) + 1
            if (ind < len(html) - 1 and html[ind] == ' ' and 
                html[ind + 1] == '<' and html[ind] != c):
                ind += 1
                
        return ind
        
    def __char_equal(self, c, html, ind):
        """
        Checks if the given character is equal to the character that represents
        the given position of the html text.

        Parameters
        ----------
        c : str
            Character that we want to check.
        html : str
            Message body represented as html.
        ind : int
            Position of the character in html.

        Returns
        -------
        bool
            Indicates if the characteres are 'equals' taking into account the
            special HTML characters.
        int
            Positon of the next character in html.

        """
        if c not in cf.SPECIAL_HTML_CHAR:
            return c == html[ind], ind + 1
        else:
            new_pos = ind + len(cf.SPECIAL_HTML_CHAR[c])
            return html.startswith(cf.SPECIAL_HTML_CHAR[c], ind), new_pos
    
    def __find_first_match(self, c, html, ind):
        """
        Finds the first character in the given html text which matches with 
        the given character.

        Parameters
        ----------
        c : str
            Character that we want to match with.
        html : str
            Message body represented as html.
        ind : int
            Position from which we will look for the match.

        Returns
        -------
        ind : int
            Position of the character of html which matches with c.

        """
        eq, _ = self.__char_equal(c, html, ind)
        while not(eq):
            if html[ind] == '<':
                ind = html.find('>', ind) + 1
                if (ind < len(html) - 1 and html[ind] == ' ' and
                    html[ind + 1] == '<' and html[ind] != c):
                    ind += 1
            else:
                ind += 1
            
            eq, _ = self.__char_equal(c, html, ind)
                
        return ind
    
    def __is_list_item(self, c, html, ind):
        """
        Checks if the character belongs to a list.

        Parameters
        ----------
        c : str
            Character of the plain text.
        html : str
            Message body represented as html.
        ind : int
            Position from which we will check it.

        Returns
        -------
        is_list_item : bool
            Indicates if the character is a list item.
        ind : int
            Position of the character of html after checking it.

        """
        is_list_item = False
        if html[ind] == '<':
            tag = self.__extract_html_tag(html, ind + 1)
            is_list_item = self.__extract_html_tag(html, ind + 1) == 'li'
        
        while (html[ind] == '<' and tag in cf.TAGS_LIST):
            ind = html.find('>', ind) + 1
            if (ind < len(html) - 1 and html[ind] == ' ' and 
                html[ind + 1] == '<' and html[ind] != c):
                ind += 1
            if html[ind] == '<':
                tag = self.__extract_html_tag(html, ind + 1)
                is_list_item = is_list_item or tag == 'li'
                
        return is_list_item, ind
    
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
        start_list_item = False
        pos = 0
        
        while pos < len(plain):
            if self.__carriage_return_followed_by_newline(pos, plain):
                pos += 1
                
            c = plain[pos]
            
            if (c == '\n' or c == ' ' or c == '*'):
                ind = self.__find_first_known_tag(c, html, ind)
                    
            if not(start_list_item):
                if (not(c.isdigit()) and  (c not in cf.SPECIAL_CHAR) and c != '\n'):
                    ind = self.__find_first_match(c, html, ind)
                        
                if (c == '-' or c == '.' or c.isdigit()):
                    ind = self.__find_first_known_tag(c, html, ind)
                    
                eq, new_ind = self.__char_equal(c, html, ind)
                if eq:
                    ind = new_ind
                    cleaned_text += c
                elif c == '\n':
                    if html[ind] == '<' and self.__is_break_line_tag(html, ind + 1):
                        cleaned_text += c
                        ind = html.find('>', ind) + 1
                    elif (html[ind] == ' ' and pos < len(plain) - 1 and 
                          plain[pos + 1].isalpha()):
                        cleaned_text += html[ind]
                        ind += 1
                elif c == '*':
                    while (html[ind] == '<' and 
                           self.__is_text_format_tag(html, ind + 1)):
                        ind = html.find('>', ind) + 1
                elif (c == '-' or c == '.' or c.isdigit()):
                    start_list_item = True
                    
                    is_list_item, ind = self.__is_list_item(c, html, ind)
                    if is_list_item:
                        cleaned_text += '\n'
            else:
                if (c != '*' and c != '\n'):
                    while html[ind] == '<':
                        ind = html.find('>', ind) + 1
                        if (ind < len(html) - 1 and html[ind] == ' ' and 
                            html[ind + 1] == '<' and html[ind] != c):
                            ind += 1
                
                eq, new_ind = self.__char_equal(c, html, ind)
                if eq:
                    cleaned_text += c
                    ind = new_ind
                    start_list_item = False
                elif (c == '*' and html[ind] == '<' and
                      self.__is_text_format_tag(html, ind + 1)):
                    ind = html.find('>', ind) + 1
                    start_list_item = False
                elif (c == '\n' and html[ind] == '<' and
                      self.__is_break_line_tag(html, ind + 1)):
                    cleaned_text += c
                    ind = html.find('>', ind) + 1
                    start_list_item = False
                
            pos += 1
            
        return cleaned_text
        
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
                if (i < n and text[i].isalpha() and new_text[-1].isalpha()):
                    new_text += ' '
                while((i + 1 < n) and text[i] == '\r' and text[i + 1] == '\n'):
                    new_text += text[i + 1]
                    i += 2
            elif (text[i] == '\n'):
                i += 1
                if (i < n and text[i].isalpha() and new_text[-1].isalpha()):
                    new_text += ' '
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
        
    def __extract_body_msg(self, prep_msg, raw_msg):
        """
        Extracts the body message from the raw message. For achieving this
        goal, this function removes the text of the replied email (if it
        exists) and the soft break lines inserted in the body.

        Parameters
        ----------
        prep_msg : dict
            Dictionary where the extracted text is going to be stored.
        raw_msg : dict
            Dictionary with the raw information of the message.

        Returns
        -------
        None.

        """
        if raw_msg['depth'] > 0:
            ind = raw_msg['bodyPlain'].find(cf.FOWARD_LINE)
            if (ind >= 0):
                # As we can't detect (without comparing it) which 
                # part of the message is originally text of the 
                # forwarded message, we delete all that part.
                raw_msg['bodyPlain'] = raw_msg['bodyPlain'][:ind]
            prep_msg['bodyPlain'] = EmailReplyParser.parse_reply(
                raw_msg['bodyPlain'])
            prep_msg['bodyPlain'] = self.__remove_header_replied(
                prep_msg['bodyPlain'])
                
            if 'bodyHtml' in raw_msg:
                prep_msg['bodyPlain'] = self.__remove_soft_breaks(
                    prep_msg['bodyPlain'], raw_msg.pop('bodyHtml'))
            elif ('plainEncoding' in raw_msg and 
                  raw_msg['plainEncoding'] == 'quoted-printable'):
                prep_msg['bodyPlain'] = self.__clean_decoded_text(
                    prep_msg['bodyPlain'])
                    
        elif 'bodyHtml' in raw_msg:
            prep_msg['bodyPlain'] = self.__remove_soft_breaks(
                raw_msg['bodyPlain'], raw_msg.pop('bodyHtml'))
        elif ('plainEncoding' in raw_msg and 
              raw_msg['plainEncoding'] == 'quoted-printable'):
            prep_msg['bodyPlain'] = self.__clean_decoded_text(
                raw_msg['bodyPlain'])
        else:
            prep_msg['bodyPlain'] = raw_msg['bodyPlain']
            
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
        prep['sender'] = raw['sender']
        prep['depth'] = raw['depth']
        prep['date'] = raw['date']
        if 'subject' in raw:
            prep['subject'] = raw['subject']
        if ('plainEncoding' in raw and raw['plainEncoding'] is not None):
            prep['plainEncoding'] = raw['plainEncoding']
        if ('bodyBase64Html' in raw):
            prep['bodyBase64Html'] = raw['bodyBase64Html']
            
    def __save_prep_msg(self, prep):
        """
        Save in the database the preprocessed message.

        Parameters
        ----------
        prep : dict
            Preprocessed message with the following estructure:
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
                'bodyHtml': string,          # Optional
                'bodyBase64Plain' : string,
                'bodyBase64Html' : string,   # Optional
                'plainEncoding' : string,    # Optional
                'charLength' : int
            }

        Returns
        -------
        None.

        """
        msg = PreprocessedMessage()
        msg.msg_id = prep['id']
        msg.threadId = prep['threadId']
        for recipient in prep['to']:
            msg.to.append(recipient)
        for recipient in prep['cc']:
            msg.cc.append(recipient)
        for recipient in prep['bcc']:
            msg.bcc.append(recipient)
        msg.sender = prep['sender']
        msg.date = prep['date']
        
        if 'subject' in prep:
            msg.subject = prep['subject']
            
        msg.depth = prep['depth']
        msg.bodyBase64Plain = prep['bodyBase64Plain']
        
        if 'plainEncoding' in prep:
            msg.plainEncoding = prep['plainEncoding']
        if 'bodyBase64Html' in prep:
            msg.bodyBase64Html = prep['bodyBase64Html']

        msg.charLength = prep['charLength']
        msg.save()
                    
    def preprocess_message(self, raw_msg, sign = None):
        """
        Obtains the extracted message and preprocessed it by extracting only
        the body message (removing the sign, the replied message, ...). Besides
        this method saves the preprocessed messages.
        
        Parameters
        ----------
        raw_msg: dict
            Extracted message which is going to be preprocessed. It has the
            following strcture:
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
                'bodyBase64Plain' : string,  # Optional
                'bodyBase64Html' : string,   # Optional
                'plainEncoding' : string,    # Optional
                'charLength' : int           # Optional
            }
        sign: str (optional)
            Sign of the person who writes the emails.
            
        Returns
        -------
        prep['id'] : str
            Message identifier.
        
        """
        if ('bodyBase64Plain' in raw_msg and 
            not(PreprocessedMessage.objects(msg_id = raw_msg['id']).first())):
            prep_msg = {}
            raw_msg['bodyPlain'] = base64.urlsafe_b64decode(
                raw_msg['bodyBase64Plain'].encode()).decode()
            
            if 'bodyBase64Html' in raw_msg:
                raw_msg['bodyHtml'] = base64.urlsafe_b64decode(
                    raw_msg['bodyBase64Html'].encode()).decode()
            self.__extract_body_msg(prep_msg, raw_msg)
            
            if sign is not None:
                prep_msg['bodyPlain'] = self.__remove_signature(
                    prep_msg['bodyPlain'], sign)
            
            prep_msg['bodyBase64Plain'] = base64.urlsafe_b64encode(
                prep_msg['bodyPlain'].encode()).decode()
                            
            
            self.__copy_metadata(prep_msg, raw_msg)
            prep_msg['charLength'] = len(prep_msg['bodyPlain'])
            
            self.__save_prep_msg(prep_msg)
            
            return prep_msg['id']