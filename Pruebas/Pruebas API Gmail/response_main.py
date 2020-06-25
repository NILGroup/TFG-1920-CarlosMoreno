from __future__ import print_function
from googleapiclient.discovery import build
import auth
import messages

SCOPES = ['https://mail.google.com/']
CLIENT_SECRET_FILE = 'credentials.json'

def main():
    """
    List the mails of a Gmail account
    """
    #Creation of an auth instance
    authInst = auth.auth(SCOPES, CLIENT_SECRET_FILE)
    service = build('gmail', 'v1', credentials=authInst.get_credentials())

    #Creation of a thread instance
    mailInst = messages.email_messages(service)
    msg_list = mailInst.get_message_list()
    ind_msg = int(input('¿Qué mensaje desea responder? '))
    mailInst.reply_message(message_id = msg_list[ind_msg]['id'],
        message_text = 'Hi Romualda,\nThanks for your message, this is an authomatic reply')

if __name__ == '__main__':
    main()