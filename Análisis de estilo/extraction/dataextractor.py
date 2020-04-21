# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 14:32:54 2019

@author: Carlos Moreno Morera
"""

from __future__ import print_function
import base64

NUM_HEADERS = 7

class DataExtractor:
    """
    The DataExtractor class performs the task of extracting the information of
    a given email.

    Attributes
    ----------
    __id: str
        Identifier of the given message.
    __thread_id: str
        Identifier of the given message's thread.
    __to: list
        List of addresses of the primary recipients of the given message.
    __cc: list
        List of addresses of others who are to receive the given message, 
        though the content of the message may not be directed at them.
    __bcc: list
        List of addresses of recipients of the given message whose addresses 
        are not to be revealed to other recipients of the message.
    __date: long
        The internal message creation timestamp (epoch ms).
    __subject: str
        Subject of the given message.
    __plain_text: str
        Body, as plain text, of the given message.
    __html_text: str
        Body, as html text, of the given message.
    __plain_encod : str
        Enconding of the plain text.
    __from: str
        Sender of the message
    __references: str
        Identifiers of previous messages of the same thread.
    """
    def __init__(self):
        """
        Class constructor.

        Returns
        -------
        Constructed DataExtractor class.

        """
        self.__id = None
        self.__thread_id = None
        self.__to = []
        self.__cc = []
        self.__bcc = []
        self.__date = None
        self.__subject = None
        self.__plain_text = None
        self.__html_text = None
        self.__plain_encod = None
        self.__from = None
        self.__references = None

    def __dec_b64(self, text):
        """
        Decode string text using the URL-and filesystem-safe alphabet.

        Parameters
        ----------
        text : str
            Text is going to be decoded.

        Returns
        -------
        str: Decoded text.
        """
        return base64.urlsafe_b64decode(text).decode('utf-8')

    def __is_there_data(self, part):
        """
        Returns whether there is data or not in the given MIME message part.

        Parameters
        ----------
        part : MIME message part
            MIME message part of which we want to know if there is data.

        Returns
        -------
        bool: whether there is data or not in the given MIME message part.

        """
        return ('body' in part and 'data' in part['body'])

    def __get_headers(self, headers):
        """
        Obtains the attributes of this class that we can find in the headers
        list of a MIME message.

        Parameters
        ----------
        headers: list
            List of MIME message headers.

        Returns
        -------
        str: header Content-Type of the MIME message.

        """
        i = 0
        found = 0
        cont_type = None
        while (i < len(headers) and found < NUM_HEADERS):
            if (headers[i]['name'] == 'Content-Type'):
                cont_type = headers[i]['value']
                found += 1
            elif (headers[i]['name'] == 'Subject'):
                self.__subject = headers[i]['value']
                found += 1
            elif (headers[i]['name'] == 'From'):
                self.__from = headers[i]['value']
                found += 1
            elif (headers[i]['name'] == 'To' 
                  and headers[i]['value'] != 'undisclosed-recipients:;'):
                self.__to = headers[i]['value'].split(',')
                found += 1
            elif (headers[i]['name'] == 'Cc'):
                self.__cc = headers[i]['value'].split(',')
                found += 1
            elif (headers[i]['name'] == 'Bcc'):
                self.__bcc = headers[i]['value'].split(',')
                found += 1
            elif (headers[i]['name'] == 'References'):
                self.__references = headers[i]['value']
                found += 1
            i += 1
        return cont_type

    def __get_Content_Type(self, message):
        """
        Gets the content type of a message or a part of a message.

        Parameters
        ----------
        message : Gmail API users.messages resource
            Message resource we want to extract the Content-Type MIME message
            header.

        Returns
        -------
        str: header Content-Type of the MIME message.

        """
        i = 0
        headers = message['headers']
        n = len(headers)
    
        while (i < n and headers[i]['name'] != 'Content-Type'):
            i = i + 1
    
        if i < n:
            return headers[i]['value']
        
    def __get_Content_Encoding(self, part):
        """
        Gets the content type of a message or a part of a message.

        Parameters
        ----------
        part : MIME part
            Message part we want to extract the Content-Transfer-Encoding MIME 
            message header.

        Returns
        -------
        str: header Content-Transfer-Encoding of the MIME message.

        """
        i = 0
        headers = part['headers']
        n = len(headers)
    
        while (i < n and headers[i]['name'] != 'Content-Transfer-Encoding'):
            i = i + 1
    
        if i < n:
            return headers[i]['value']

    def __get_part_type(self, part):
        """
        Gets the MIME type of the given MIME message part.

        Parameters
        ----------
        part: dict
            MIME message part.

        Returns
        -------
        str: type of the MIME message part.
        """
        if ('mimeType' in part):
            return part['mimeType']
        else:
            return self.__get_Content_Type(part)

    def __is_type(self, t, part, p_type):
        """
        Return whether or not the given part is a leaf of MIME type tree with
        the type t.

        Parameters
        ----------
        t: str
            Type that we want to check.
        part: dict
            MIME message part.
        p_type: str
            Type of the given MIME message part.

        Returns
        -------
        bool: whether or not the given part has the type t.
        """
        return p_type.startswith(t) and self.__is_there_data(part)
    
    def __clean_html_text(self, text):
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
                    new_text = new_text + text[i] + text[i + 1]
                    i += 2
            else:
                new_text += text[i]
                i += 1
    
        return new_text

    def __get_text_content(self, msg_parts):
        """
        Get the body of the message as a plain text and as a html text if they
        exist. This function visits the tree nodes following the pre-order 
        traversal until it finds what it is looking for.

        Parameters
        ----------
        msg_parts: list.
            List of MIME message parts.

        Returns
        -------
        None.

        """
        i = 0
        n = len(msg_parts)
        plain_found = False
        html_found = False
    
        while (not(plain_found) or not(html_found) and i < n):
            part = msg_parts[i]

            p_type = self.__get_part_type(part)
            if (p_type is not None):
                if (p_type.startswith('multipart') and 'parts' in part):
                    self.__get_text_content(part['parts'])
                elif (self.__is_type('text/plain', part, p_type)):
                    self.__plain_text = self.__dec_b64(part['body']['data'])
                    self.__plain_encod = self.__get_Content_Encoding(part)
                    plain_found = True
                elif (self.__is_type('text/html', part, p_type)):
                    if (self.__get_Content_Encoding(part) == 'quoted-printable'):
                        self.__html_text = self.__clean_html_text(
                            self.__dec_b64(part['body']['data']))
                    else:
                        self.__html_text = self.__dec_b64(part['body']['data'])
                    html_found = True
    
            i += 1
    
    def __get_message_text(self, message):
        """
        Obtains the message body as a plaint text and html text if they exist.

        Parameters
        ----------
        message: Gmail API users.messages resource
            Message that we want to extract its body.

        Returns
        -------
        None.
        """
        pld = message['payload']
        mimetype = self.__get_headers(pld['headers'])
        if 'mimeType' in pld:
            mimetype = pld['mimeType']

        if mimetype is not None:
            if mimetype.startswith('multipart/'):
                self.__get_text_content(pld['parts'])
            elif (self.__is_type('text/plain', pld, mimetype)):
                self.__plain_text = self.__dec_b64(pld['body']['data'])
                self.__plain_encod = self.__get_Content_Encoding(pld)
            elif (self.__is_type('text/html', pld, mimetype)):
                if (self.__get_Content_Encoding(pld) == 'quoted-printable'):
                    self.__html_text = self.__clean_html_text(
                        self.__dec_b64(pld['body']['data']))
                else:
                    self.__html_text = self.__dec_b64(pld['body']['data'])

    def set_new_message(self, msg):
        """
        Sets a new message to extract its data.

        Parameters
        ----------
        msg : Gmail API users.messages resource
            Message resource we want to extract the information.

        Returns
        -------
        None.
        """
        self.__id = msg['id']
        self.__thread_id = msg['threadId']
        self.__to = []
        self.__cc = []
        self.__bcc = []
        self.__date = msg['internalDate']
        self.__subject = None
        self.__plain_text = None
        self.__plain_encod = None
        self.__html_text = None
        self.__from = None
        self.__references = None
        self.__get_message_text(msg)

    def get_subject(self):
        """
        Obtains the subject of the message.

        Returns
        -------
        str: subject of the message.

        """
        return self.__subject

    def get_plain_text(self):
        """
        Obtains the body of the message as a plain text.

        Returns
        -------
        str: body of the message.

        """
        return self.__plain_text
    
    def get_plain_encod(self):
        """
        Obtains the encoding of the body of the message as a plain text.

        Returns
        -------
        str: encoding of the body of the message.

        """
        return self.__plain_encod

    def get_html_text(self):
        """
        Obtains the body of the message as a html text.

        Returns
        -------
        str: body of the message.

        """
        return self.__html_text
    
    def get_references(self):
        """
        Obtains the references of the message.

        Returns
        -------
        str: references of the message.

        """
        return self.__references

    def insert_metadata(self, msg):
        """
        Inserts the metadata of the message in the given MessageInfo object.
        
        Parameters
        ----------
        msg: MessageInfo
            MessageInfo object where the data is going to be stored.

        Returns
        -------
        None.

        """
        msg.msg_id = self.__id
        msg.thread_id = self.__thread_id
        for recipient in self.__to:
            msg.to.append(recipient)
        for recipient in self.__cc:
            msg.cc.append(recipient)
        for recipient in self.__bcc:
            msg.bcc.append(recipient)
        msg.sender = self.__from
        msg.date = self.__date