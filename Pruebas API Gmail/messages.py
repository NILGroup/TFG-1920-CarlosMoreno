from __future__ import print_function
import base64
from email.mime.text import MIMEText
from googleapiclient.errors import HttpError

class email_messages:
    def __init__(self, service):
        self.service = service

    def get_message_list(self, user_id='me'):
        """
        Print all the messages in inbox
        """
        msg_list = self.service.users().messages().list(userId=user_id, labelIds = ['INBOX']).execute().get('messages', [])
        for i in range(0, len(msg_list)):
            mdata = self.service.users().messages().get(userId=user_id, id=msg_list[i]['id']).execute()

            #Export sections of the list headers
            head_sect = {}
            for j in range (0, len(mdata['payload']['headers'])):
                head_sect[mdata['payload']['headers'][j]['name']] = j

            print('%d.- Message subject: %s' %
                  (i, mdata['payload']['headers'][head_sect['Subject']]['value']))
            head_sect.clear()

        return msg_list

    def reply_message(self, message_id, message_text, user_id = 'me'):
        rep_msg = self.service.users().messages().get(id = message_id, userId = user_id).execute()
        payload_h = rep_msg['payload']['headers']
        #Export sections of the list headers
        head_sect = {}
        for i in range(0, len(payload_h)):
            head_sect[payload_h[i]['name']] = i

        message =  MIMEText(message_text)
        message['To'] = payload_h[head_sect['From']]['value']
        message['From'] = self.service.users().getProfile(userId = 'me').execute()['emailAddress']
        message['Subject'] = payload_h[head_sect['Subject']]['value']
        message['In-Reply-To'] = payload_h[head_sect['Message-ID']]['value']
        message['References'] = payload_h[head_sect['Message-ID']]['value']

        head_sect.clear()

        message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
        message['threadId'] = rep_msg['threadId']
        try:
            msg = (self.service.users().messages().send(userId=user_id, body=message)
                       .execute())
            print('Message Id: %s' % msg['id'])
            return msg
        except HttpError as error:
            print('An error occurred: %s' % error)