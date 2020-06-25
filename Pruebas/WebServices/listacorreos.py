#!C:\Users\Carlos\AppData\Local\Programs\Python\Python37-32\python.exe
from __future__ import print_function
from googleapiclient.discovery import build
import auth
import gmailList
import json

SCOPES = ['https://mail.google.com/']
CLIENT_SECRET_FILE = 'credentials.json'

#Creation of an auth instance
authInst = auth.auth(SCOPES, CLIENT_SECRET_FILE)
service = build('gmail', 'v1', credentials=authInst.get_credentials())
print(json.dumps(gmailList.get_gmail_list(service = service)))