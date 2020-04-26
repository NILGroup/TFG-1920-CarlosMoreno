# -*- coding: utf-8 -*-
"""
Created on Sun Apr 26 23:11:46 2020

@author: Carlos
"""

import os, sys
initial_dir = os.getcwd()
os.chdir('../')
if not(os.getcwd() in sys.path):
    sys.path.append(os.getcwd())

from flask import Flask, jsonify, request
from typocorrection.typocorrector import TypoCorrector
from initdb import init_db
from confanalyser import NLP

os.chdir(initial_dir)

app = Flask(__name__)
typocorrector = TypoCorrector(NLP)

@app.route('/typocorrector/correct', methods=['POST'])
def correct_message():
    """
    Checks the typographic errors of the preprocessed message given by the 
    post method.

    Returns
    -------
    json: Dictionary in json format which has the result of checking the
    typographic errors.

    """
    msg = request.json['message']
    
    prep = {
        'threadId': msg['threadId'],
        'to': msg['to'],
        'cc': msg['cc'],
        'bcc': msg['bcc'],
        'sender': msg['sender'],
        'depth': msg['depth'],
        'date': msg['date'],
        'charLength': msg['charLength']
    }
    if ('_id' in msg) and (msg['_id'] is not None):
        prep['id'] = msg['_id']
    elif ('id' in msg) and (msg['id'] is not None):
        prep['id'] = msg['id']
    
    if ('subject' in msg) and (msg['subject'] is not None):
        prep['subject'] = msg['subject']
    if ('bodyBase64Plain' in msg) and (msg['bodyBase64Plain'] is not None):
        prep['bodyBase64Plain'] = msg['bodyBase64Plain']
    if ('bodyBase64Html' in msg) and (msg['bodyBase64Html'] is not None):
        prep['bodyBase64Html'] = msg['bodyBase64Html']
    if ('plainEncoding' in msg) and (msg['plainEncoding'] is not None):
        prep['plainEncoding'] = msg['plainEncoding']
    if ('bodyPlain' in msg) and (msg['bodyPlain'] is not None):
        prep['bodyPlain'] = msg['bodyPlain']
    if ('corrections' in msg) and (msg['corrections'] is not None):
        prep['corrections'] = msg['corrections']
        
    return jsonify(typocorrector.correct_msg(prep, request.json['index']))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)