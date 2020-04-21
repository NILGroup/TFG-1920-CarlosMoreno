# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 13:49:01 2020

@author: Carlos
"""

from flask import Flask, jsonify, request
from preprocessor import Preprocessor
from confanalyser import NLP

app = Flask(__name__)
preprocessor = Preprocessor(NLP)

@app.route('/preprocessor', methods=['POST'])
def preprocess_message():
    msg = request.json['message']
    
    raw = {
        'id': msg['msg_id'],
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
        
    return jsonify(preprocessor.preprocess_message(raw, request.json['sign']))

if __name__ == '__main__':
    app.run(debug=True)