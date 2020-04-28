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
    
    msg['id'] = msg['_id']
    del msg['_id']
    
    return jsonify({'id' : 
                    preprocessor.preprocess_message(msg, request.json['sign'])})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)