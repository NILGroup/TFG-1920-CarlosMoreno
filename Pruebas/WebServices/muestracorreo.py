#!C:\Users\Carlos\AppData\Local\Programs\Python\Python37-32\python.exe
from __future__ import print_function
from googleapiclient.discovery import build
import auth
import sys
import gmailText
import json

SCOPES = ['https://mail.google.com/']
CLIENT_SECRET_FILE = 'credentials.json'

#Creation of an auth instance
authInst = auth.auth(SCOPES, CLIENT_SECRET_FILE)
service = build('gmail', 'v1', credentials=authInst.get_credentials())

#Le estás dando el id del primer mensaje thread no del mensaje (cambiar)
msg = service.users().messages().get(userId = 'me', id = sys.argv[1]).execute()
subject = ""
sender = ""
for header in msg['payload']['headers']:
    if header['name'] == 'Subject':
        subject = header['value']
    elif header['name'] == 'From' :
        sender = header['value']
email_info = {'Subject' : subject, 'From' : sender, 'Text' : gmailText.get_message_text(msg)}
print(json.dumps(email_info))