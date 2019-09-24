from __future__ import print_function
from googleapiclient.discovery import build
import auth
import drafts

SCOPES = ['https://mail.google.com/']
CLIENT_SECRET_FILE = 'credentials.json'

def main():
    """
    Send an email from a Gmail account
    """
    #Creation of an auth instance
    authInst = auth.auth(SCOPES, CLIENT_SECRET_FILE)
    service = build('gmail', 'v1', credentials=authInst.get_credentials())

    #Creation of a draft instance
    draftInst = drafts.drafts(service)
    message1 = draftInst.create_message('ferrerromualda@gmail.com',
            'pepitosuarezgerminio@gmail.com', 'Test with draft',
            'Hi there, this is the first draft created with Python')
    message2 = draftInst.create_message('ferrerromualda@gmail.com',
            '', '', 'Hi there, this is the second draft created with Python')
    draftInst.create_draft('me', message1)
    draftInst.create_draft('me', message2)
    draftInst.list_drafts('me')

if __name__ == '__main__':
    main()