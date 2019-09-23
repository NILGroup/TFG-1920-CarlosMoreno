from __future__ import print_function
from googleapiclient.discovery import build
import auth

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
CLIENT_SECRET_FILE = 'credentials.json'

def main():
    """
    Send an email from a Gmail account
    """
    #Creation of an auth instance
    authInst = auth.auth(SCOPES, CLIENT_SECRET_FILE)
    service = build('gmail', 'v1', credentials=authInst.get_credentials())

    # Call the Gmail API
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])

    if not labels:
        print('No labels found.')
    else:
        print('Labels:')
        for label in labels:
            print(label['name'])

if __name__ == '__main__':
    main()