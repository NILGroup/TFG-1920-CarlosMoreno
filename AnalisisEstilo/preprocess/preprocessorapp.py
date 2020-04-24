# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 13:49:01 2020

@author: Carlos
"""
import os, sys
initial_dir = os.getcwd()
os.chdir('../')
if not(os.getcwd() in sys.path):
    sys.path.append(os.getcwd())

from flask import Flask, jsonify, request
from preprocess.preprocessor import Preprocessor
from initdb import init_db

os.chdir(initial_dir)

app = Flask(__name__)
preprocessor = Preprocessor()

@app.route('/preprocessor', methods=['POST'])
def preprocess_message():
    """
    Preprocess the extracted message given by the post method.

    Returns
    -------
    json: Dictionary in json format which only has the 'id' of the preprocessed
    message.

    """
    msg = request.json['message']
    
    raw = {
        'id': msg['_id'],
        'threadId': msg['thread_id'],
        'to': msg['to'],
        'cc': msg['cc'],
        'bcc': msg['bcc'],
        'from': msg['sender'],
        'depth': msg['depth'],
        'date': msg['date'],
        'charLength': msg['charLength']
    }
    
    if ('subject' in msg) and (msg['subject'] is not None):
        raw['subject'] = msg['subject']
    if ('bodyBase64Plain' in msg) and (msg['bodyBase64Plain'] is not None):
        raw['bodyBase64Plain'] = msg['bodyBase64Plain']
    if ('bodyBase64Html' in msg) and (msg['bodyBase64Html'] is not None):
        raw['bodyBase64Html'] = msg['bodyBase64Html']
    if ('plainEncoding' in msg) and (msg['plainEncoding'] is not None):
        raw['plainEncoding'] = msg['plainEncoding']
        
    return jsonify({'id' : 
                    preprocessor.preprocess_message(raw, request.json['sign'])})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)