# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 21:03:09 2020

@author: Carlos
"""

import os, sys
initial_dir = os.getcwd()
os.chdir('../')
if not(os.getcwd() in sys.path):
    sys.path.append(os.getcwd())

from flask import Flask, request
from stylemeasuring.stylemeter import StyleMeter
from initdb import init_db
from confanalyser import NLP

os.chdir(initial_dir)

app = Flask(__name__)
stylemeter = StyleMeter(NLP)

@app.route('/stylemeter', methods=['POST'])
def measure_style():
    """
    Measures the writting style of the given message.

    Returns
    -------
    str: Message which confirms that it was successfully measured.

    """
    msg = request.json['message']
    
    msg['id'] = msg['_id']
    del msg['_id']
    
    stylemeter.measure_style(msg)
    
    return "Successfully measured."

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port = 6000)