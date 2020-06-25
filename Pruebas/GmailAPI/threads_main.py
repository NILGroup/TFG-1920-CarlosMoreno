from __future__ import print_function
from googleapiclient.discovery import build
import auth
import threads

SCOPES = ['https://mail.google.com/']
CLIENT_SECRET_FILE = 'credentials.json'

def main():
    """
    List the threads of a Gmail account
    """
    #Creation of an auth instance
    authInst = auth.auth(SCOPES, CLIENT_SECRET_FILE)
    service = build('gmail', 'v1', credentials=authInst.get_credentials())

    #Creation of a thread instance
    threadInst = threads.email_threads(service)
    threadInst.show_chatty_threads()

if __name__ == '__main__':
    main()