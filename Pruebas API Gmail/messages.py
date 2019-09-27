from __future__ import print_function

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