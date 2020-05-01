# -*- coding: utf-8 -*-
"""
Created on Sun Apr 26 23:11:46 2020

@author: Carlos Moreno Morera
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
    
    if ('_id' in msg) and (msg['_id'] is not None):
        msg['id'] = msg['_id']
        del msg['_id']
        
    return jsonify(typocorrector.correct_msg(msg, request.json['index']))

@app.route('/typocorrector/saveoov', methods=['POST'])
def save_oov():
    """
    Saves a new token in the mongoDB which Spacy's model has recognised as
    a typographic error. It is given by the post method.

    Returns
    -------
    str: Message which confirms that it was successfully saved.

    """
    typocorrector.save_oov(request.json)
    return 'Successfully saved'

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port = 4000)