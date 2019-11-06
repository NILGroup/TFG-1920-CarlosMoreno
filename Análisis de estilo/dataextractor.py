from __future__ import print_function
import base64

class DataExtractor:
    def __init__(self, msg):
        self.__plain_text = None
        self.__html_text = None
        self.__get_message_text(msg)

    def __dec_b64(text):
        return base64.urlsafe_b64decode(text).decode('utf-8')

    def __is_there_data(self, part):
        return ('body' in part and 'data' in part['body'])

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
        finded = False
        text = None
    
        while (not(finded) and i < n):
            part = msg_parts[i]
    
            if 'mimeType' in msg_parts[i]:
                if (part['mimeType'].startswith('multipart') and 'parts' in part):
                    text = get_text_content(part['parts'])
                elif (part['mimeType'] == 'text/plain' and ('body' in part) and
                'data' in part['body']):
                    text = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
            else:
                cont_type = get_Content_Type(part)
                if ((cont_type is not None) and cont_type.startswith('text/plain')
                and ('body' in part) and 'data' in part['body']):
                    text = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                elif ((cont_type is not None) and cont_type.startswith('multipart') and
                'parts' in part):
                    text = get_text_content(part['parts'])
    
            finded = text is not None
            if not finded:
                i = i + 1
    
        return text
    
    def __clean_decoded_text(self, text):
        new_text = ""
        i = 0
        n = len(text)
        while i < n:
            if (text[i] == '\r' and (i + 1 < n) and text[i + 1] == '\n'):
                i = i + 2
                while((i + 1 < n) and text[i] == '\r' and text[i + 1] == '\n'):
                    new_text = new_text + text[i] + text[i + 1]
                    i = i + 2
            else:
                new_text = new_text + text[i]
                i = i + 1
    
        return new_text
    
    def __get_message_text(self, message):
        pld = message['payload']
        mimetype = ""
        if 'mimeType' in pld:
            mimetype = pld['mimeType']
        else:
            mimetype = self.__get_Content_Type(pld)

        if mimetype.startswith('multipart/'):
            self.__get_text_content(pld['parts'])
        elif (mimetype.startswith('text/plain') and self.__is_there_data(pld)):
            self.__plain_text = self.__clean_decoded_text(pld['body']['data'])
        elif (mimetype.startswith('text/html') and self.__is_there_data(pld)):
            self.__html_text = self.__clean_decoded_text(pld['body']['data'])
        else:
            return None