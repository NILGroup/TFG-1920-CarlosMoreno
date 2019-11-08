from __future__ import print_function
import base64

NUM_HEADERS = 5

class DataExtractor:
    def __init__(self, msg):
        self.__id = msg['id']
        self.__thread_id = msg['threadId']
        self.__to = []
        self.__cc = []
        self.__bcc = []
        self.__date = msg['internalDate']
        self.__subject = None
        self.__plain_text = None
        self.__html_text = None
        self.__get_message_text(msg)

    def __dec_b64(self, text):
        return base64.urlsafe_b64decode(text).decode('utf-8')

    def __is_there_data(self, part):
        return ('body' in part and 'data' in part['body'])

    def __get_headers(self, headers):
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
            elif (headers[i]['name'] == 'To'):
                self.__to = headers[i]['value'].split(',')
                found += 1
            elif (headers[i]['name'] == 'Cc'):
                self.__cc = headers[i]['value'].split(',')
                found += 1
            elif (headers[i]['name'] == 'Bcc'):
                self.__bcc = headers[i]['value'].split(',')
                found += 1
            i += 1
        return cont_type


    def __get_Content_Type(self, message):
        """
        It gets the content type of a message or a part of a message.
        """
        i = 0
        headers = message['headers']
        n = len(headers)
    
        while (i < n and headers[i]['name'] != 'Content-Type'):
            i = i + 1
    
        if i < n:
            return headers[i]['value']
    
    def __get_text_content(self, msg_parts):
        """
        If there is a message part of the text/plain type it returns its content decoded.
        Otherwise it returns None.
    
        This function visits the tree nodes following the pre-order traversal until it
        finds what it is looking for.
    
        msg_parts is a list of the parts of the message
        """
        i = 0
        n = len(msg_parts)
        plain_found = False
        html_found = False
    
        while (not(plain_found) and not(html_found) and i < n):
            part = msg_parts[i]

            if 'mimeType' in msg_parts[i]:
                if (part['mimeType'].startswith('multipart') and 'parts' in part):
                    self.__get_text_content(part['parts'])
                elif (part['mimeType'] == 'text/plain' and self.__is_there_data(part)):
                    self.__plain_text = self.__dec_b64(part['body']['data'])
                    plain_found = True
                elif (part['mimeType'] == 'text/html' and self.__is_there_data(part)):
                    self.__html_text = self.__dec_b64(part['body']['data'])
                    html_found = True
            else:
                cont_type = self.__get_Content_Type(part)
                if ((cont_type is not None) and cont_type.startswith('text/plain')
                and self.__is_there_data(part)):
                    self.__plain_text = self.__dec_b64(part['body']['data'])
                    plain_found = True
                elif ((cont_type is not None) and cont_type.startswith('text/html')
                and self.__is_there_data(part)):
                    self.__html_text = self.__dec_b64(part['body']['data'])
                    html_found = True
                elif ((cont_type is not None) and cont_type.startswith('multipart') and
                'parts' in part):
                    self.__get_text_content(part['parts'])
    
            i += 1
    
    def __clean_decoded_text(self, text):
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
    
    def __get_message_text(self, message):
        pld = message['payload']
        mimetype = self.__get_headers(pld['headers'])
        if 'mimeType' in pld:
            mimetype = pld['mimeType']

        if mimetype.startswith('multipart/'):
            self.__get_text_content(pld['parts'])
        elif (mimetype.startswith('text/plain') and self.__is_there_data(pld)):
            self.__plain_text = self.__clean_decoded_text(pld['body']['data'])
        elif (mimetype.startswith('text/html') and self.__is_there_data(pld)):
            self.__html_text = self.__clean_decoded_text(pld['body']['data'])
        else:
            return None