from __future__ import print_function
from googleapiclient.discovery import build
import auth
import SendGmail

SCOPES = ['https://mail.google.com/']
CLIENT_SECRET_FILE = 'credentials.json'

def main():
    """
    Send an email from a Gmail account
    """
    #Creation of an auth instance
    authInst = auth.auth(SCOPES, CLIENT_SECRET_FILE)
    service = build('gmail', 'v1', credentials=authInst.get_credentials())

    #Creation of a sendGmail instance
    sendInst = SendGmail.sendGmail(service)
    message = sendInst.create_message_with_attachment('ferrerromualda@gmail.com',
            'pepitosuarezgerminio@gmail.com', 'Test 1',
            'Hi there, this is the first email sent with Python', 'foto_a_enviar.jpg')
    sendInst.send_message('me', message)

if __name__ == '__main__':
    main()