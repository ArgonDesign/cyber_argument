#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ******************************************************************************
# Argon Design Ltd. Project P9000 Argon
# (c) Copyright 2018 Argon Design Ltd. All rights reserved.
#
# Module : cyber_argument
# Author : Steve Barlow
# $Id: cyberarg_google.py 22575 2018-03-01 14:28:56Z sjb $
# ******************************************************************************

"""Action for Google Assistant to have an argument with Amazon Alexa.

This code forms a web server which responds to JSON service requests from Google
Assistant and returns a JSON response with the text to be spoken.
"""

# Useful websites:
# https://github.com/treethought/flask-assistant

from __future__ import print_function
from flask import Flask, request
from flask_assistant import Assistant, ask, tell
import os.path
import logging, logging.handlers
import argument.arguer

app = Flask(__name__)
assist = Assistant(app, route='/')

busy_response = 'My arguer is busy at the moment. Please try again later'
goodbye_text  = 'Goodbye!'

def setUpLogging():
    filename = 'cyberarg_google.log'
    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    print('Logging to {0} / {1}.1'.format(filepath, filename))
    logHandler = logging.handlers.RotatingFileHandler(filepath, maxBytes=100*1024*1024, backupCount=1) 
    logHandler.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(asctime)s] - %(levelname)s - %(message)s', '%d/%b/%Y %H:%M:%S')
    logHandler.setFormatter(formatter)
    app.logger.addHandler(logHandler)
    app.logger.setLevel(logging.INFO)
    # Werkzeug logging still comes out to stdout
 
def log(text):
    if 'X-Forwarded-For' in request.headers:
        ip = request.headers['X-Forwarded-For']
    else:
        ip = request.remote_addr
    app.logger.info('{0:15} {1}'.format(ip, text))

@assist.action('WelcomeIntent')
def WelcomeIntent():
    openingPhrase = argument.arguer.startArgument('google')
    if openingPhrase is None:
        response = busy_response
        log('WelcomeIntent Output: "{0}"'.format(response))
        return tell(response)
    else:
        response = openingPhrase
        log('WelcomeIntent Output: "{0}"'.format(response))
        return ask(response)

@assist.action('AccusationIntent')
def AccusationIntent(AccusationWords):
    if AccusationWords is None: # This catch may not be necessary
        AccusationWords = ''
    AccusationWords = AccusationWords.encode('utf-8')
    response, noReply = argument.arguer.getNextResponse(AccusationWords)
    log('AccusationIntent Input: "{0}"'.format(AccusationWords))
    log('AccusationIntent Output: "{0}"'.format(response))
    if noReply:
        return tell(response)
    else:
        return ask(response)

@assist.action('CancelIntent')
def CancelIntent():
    log('CancelIntent')
    argument.arguer.stopArgument()
    return tell(goodbye_text)

if __name__ == '__main__':
    setUpLogging()
    argument.arguer.initArguer()
    app.run(debug=False, port=5011)
