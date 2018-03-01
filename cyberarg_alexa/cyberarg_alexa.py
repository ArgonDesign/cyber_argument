#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ******************************************************************************
# Argon Design Ltd. Project P9000 Argon
# (c) Copyright 2018 Argon Design Ltd. All rights reserved.
#
# Module : cyber_argument
# Author : Steve Barlow
# $Id: cyberarg_alexa.py 22575 2018-03-01 14:28:56Z sjb $
# ******************************************************************************

"""Skill for Amazon Alexa to have an argument with Google Assistant.

This code forms a web server which responds to JSON service requests from Alexa
and returns a JSON response with the text to be spoken.
"""

# Useful websites
# https://github.com/johnwheeler/flask-ask

from __future__ import print_function
from flask import Flask, request, render_template
from flask_ask import Ask, question, statement
import os.path
import logging, logging.handlers
import argument.arguer

app = Flask(__name__)
ask = Ask(app, '/')

busy_response = 'My arguer is busy at the moment. Please try again later'
reprompt_start = 'I said: '
help_text = 'This skill only works if it has a Google Home to talk to. \
Say "next" after each statement to step through both sides of an argument without one.' 
goodbye_text  = 'Goodbye!'

def setUpLogging():
    filename = 'cyberarg_alexa.log'
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

@ask.launch
def launch():
    openingPhrase = argument.arguer.startArgument('alexa')
    if openingPhrase is None:
        response = busy_response
        log('Launch Output: "{0}"'.format(response))
        return statement(response).simple_card('Cyber Argument', response)
    else:
        response = openingPhrase
        log('Launch Output: "{0}"'.format(response))
        return question(response).reprompt(reprompt_start + response).simple_card('Cyber Argument', response)

@ask.intent('AccusationIntent')
def AccusationIntent(AccusationWords):
    if AccusationWords is None:
        AccusationWords = ''
    AccusationWords = AccusationWords.encode('utf-8')
    response, noReply = argument.arguer.getNextResponse(AccusationWords)
    log('AccusationIntent Input: "{0}"'.format(AccusationWords))
    log('AccusationIntent Output: "{0}"'.format(response))
    if noReply:
        return statement(response).simple_card('Cyber Argument', response)
    else:
        return question(response).reprompt(reprompt_start + response).simple_card('Cyber Argument', response)

@ask.intent('AMAZON.HelpIntent')
def help():
    log('AMAZON.HelpIntent')
    return question(help_text).reprompt(help_text).simple_card('Help', help_text)

@ask.intent('AMAZON.StopIntent')
def stop():
    log('AMAZON.StopIntent')
    return goodbye()

@ask.intent('AMAZON.CancelIntent')
def cancel():
    log('AMAZON.CancelIntent')
    return goodbye()

def goodbye():
    argument.arguer.stopArgument()
    return statement(goodbye_text).simple_card('Session Ended', goodbye_text)

@ask.session_ended
def session_ended():
    return '{}', 200

if __name__ == '__main__':
    setUpLogging()
    argument.arguer.initArguer()
    app.run(debug=False, port=5010)
