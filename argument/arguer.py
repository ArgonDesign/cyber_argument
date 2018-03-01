#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ******************************************************************************
# Argon Design Ltd. Project P9000 Argon
# (c) Copyright 2018 Argon Design Ltd. All rights reserved.
#
# Module : cyber_argument
# Author : Steve Barlow
# $Id: arguer.py 22575 2018-03-01 14:28:56Z sjb $
# ******************************************************************************

"""
Provide the statements in an argument between Alexa and Google one by one.

The servers responding to Alexa and Google requests are expected to be running
as separate programs and both including the arguer as a library. The arguer
enforces a lock so only one argument can be going on at a time. This is
necessary as otherwise we wouldn't know which devices should correspond. The
device that starts the argument audibly triggers the second device to run the
argument skill/app to reply so we then know these two devices are paired.

The argument can be started by either Alexa or Google. The device starting the
argument calls startArgument(assistant). 'assistant' specifies whether it is an
'alexa' or a 'google'. If the arguer is busy this call returns None, otherwise
it locks the arguer and returns a statement to trigger the alternate device. The
statement is one picked randomly from the set of responses in the YAML file
argument_data/OpeningPhrases.yml. These statements mustn't just open the
skill/app as that would generate another call to startArgument() but must
instead ask it to respond to a request. For instance 'Alexa, ask Cyber Argument
to reply' or 'Alexa, tell Cyber Argument to argue with me'.

The replying device should call getNextResponse(accusationWords) for its first
statement. Then each device should call this same function as it is triggered to
work through the argument. The function doesn't mind which device consumes each
step. 'accusationWords' is an optional parameter with the text that was heard
that could be used to craft dynamic replies in the future. getNextResponse()
returns a tuple of a response and a bool that indicates if no reply is expected.
The last two calls to getNextResponse() will each return True. The last response
is always a blank response. This ensures both devices close at almost the same
time.

To cut short an argument part way through (for instance if the user says "Stop")
call stopArgument().

The argument itself is chosen randomly from the arguments in the argument_data
directory. Arguments can be either a text file of responses or a Python
program that generates responses.

To make sure Google and Alexa always have their correct places in the argument,
whichever starts it, if Alexa starts the argument, a special neutral response
will be returned for Google from the google_interposer list in OpeningPhrases.yml.
This means the first response of the argument proper is always said by Alexa.

When the argument is finished (i.e. when the last response has been returned by
getNextResponse()) the lock is released. There is also a timeout mechanism so
the lock will be released if the argument is stopped part way through and no
further calls to getNextResponse() occur. The lock can also be manually cleared
by calling initArguer().

Example usage:
  import argument.arguer
  argument.arguer.initArguer()
  openingPhrase = argument.arguer.startArgument('alexa')
    - None indicates arguer is busy
  ...
  response, noReply = argument.arguer.getNextResponse()
  ...
"""

from __future__ import print_function
import os, os.path
import random
import time
import yaml

myDir = os.path.dirname(os.path.realpath(__file__))
argInfoFile = os.path.join(myDir, 'argInfo')
EXPIRY_TIME = 60.0
argDataDir = os.path.join(myDir, 'argument_data')
openingPhrasesFile = os.path.join(argDataDir, 'OpeningPhrases.yml')

random.seed(None)

# Force values for testing. Change from None to a number (starting from 0)
TEST_FIX_OPENING_PHRASE = None
TEST_FIX_GOOGLE_INTERPOSER = None
TEST_FIX_ARGFILE_NUM = None

# ---------------------------------------------------------------------------------------
# Private helper functions

# Read data structure from OpeningPhrases.yml
# Structure is a dict of 3 lists - 'alexa', 'google' and 'google_interposer'
def _readOpeningPhrases():
    with open(openingPhrasesFile, 'rt') as f:
        data = yaml.load(f)
    # Make sure any unicode is converted to utf-8
    # All Flask code works with utf-8 strings not unicode
    for key in data:
        data[key] = [s.encode('utf-8') for s in data[key]]
    return data

# Get list of argument files in argument_data. Each is returned as a full path
def _getListOfArgFiles():
    argExtensions = ['.txt', '.py']
    argFiles = [os.path.join(argDataDir, f) \
        for f in os.listdir(argDataDir) \
        if os.path.splitext(f)[1].lower() in argExtensions]
    return sorted(argFiles)

# Get responses from a text argument file as a list, ignoring blank lines, comments
# and removing speaker labels if present
def _getTextLines(argFile):
    # Read file removing blank lines and comments
    with open(argFile, 'rt') as f:
        lines = []
        for line in f:
            strippedLine = line.strip()
            if strippedLine == '': # Blank line
                continue
            if strippedLine.startswith('#'): # A comment
                continue
            lines.append(strippedLine)

    # Decide if text has speaker labels
    linesWithColons = 0
    for l in lines:
        if ':' in l:
            linesWithColons += 1
    hasSpeakerLabels = linesWithColons > len(lines) / 2

    # If speaker labels, remove them
    if hasSpeakerLabels:
        lines = [l.split(':',1)[-1].strip() for l in lines]

    return lines

# Get argument file name and current response number from argInfo file
# The argInfo file existing is used as a lock
# Returns (None, None) if argInfo is not present or expired
def _getArgInfo():
    try:
        with open(argInfoFile, 'rt') as f:
            argFile = f.readline().strip()
            n = int(f.readline().strip())
            expiryTime = float(f.readline().strip())
    except:
        # There's no argInfo file or it is corrupt
        return None, None

    if time.time() > expiryTime:
        return None, None
        
    return argFile, n

# Create argInfo file with argument file name and current response number
def _setArgInfo(argFile, n):
    with open(argInfoFile, 'wt') as f:
        print(argFile, file = f)
        print(n, file = f)
        print(time.time() + EXPIRY_TIME, file = f)


# ---------------------------------------------------------------------------------------
# Public functions

def initArguer():
    """
    Initialise the arguer.

    This simply involves deleting the argInfo file if it is present to release any
    hanging lock.
    """
    try:
        os.remove(argInfoFile)
    except:
        pass

def startArgument(assistant, argN=None):
    """
    Start a new argument.

    Starts a new argument and returns the opening phrase that is used to trigger the
    opposite assistant. 'assistant' is the type of assistant that has started the
    argument and must be one of 'alexa' or 'google'. 'argN' is an optional parameter
    which forces a specific argument (in the order that the files are listed) rather
    than a random choice. If the arguer is already in use, returns None.
    """
    assert assistant in ['alexa', 'google']
    
    # Return None if arguer already in use
    argFile, n = _getArgInfo()
    if argFile is not None:
        return None

    # Create argInfo file - acts as a lock file and stores which argument and where we are in it        
    argFiles = _getListOfArgFiles()
    if argN is not None:
        argFile = argFiles[argN]
    else:
        if TEST_FIX_ARGFILE_NUM is not None:
            argFile = argFiles[TEST_FIX_ARGFILE_NUM]
        else:
            argFile = random.choice(argFiles)

    n = {'alexa':-1, 'google':0}[assistant]
    _setArgInfo(argFile, n)

    data = _readOpeningPhrases()
    phrases = data[assistant]
    if TEST_FIX_OPENING_PHRASE is not None:
        openingPhrase = phrases[TEST_FIX_OPENING_PHRASE]
    else:
        openingPhrase = random.choice(phrases)
    
    return openingPhrase

def getNextResponse(accusationWords=''):
    """
    Get the next response in an ongoing argument.
    
    Each call delivers the next response in sequence. Returns a tuple of
    (response, noReply). NoReply is a bool indicating that the server should
    mark to Alexa/Google that this response should terminate the interaction.
    The last statement of the argument has noReply set. The next call returns
    a blank response ('') that also has noReply set. This means both devices
    will close at almost the same time.
    
    If this function is incorrectly called when there is no argument in
    progress, it returns the response 'Bye' with noReply set.
    """
    argFile, n = _getArgInfo()
    if argFile is None:
        return ('Bye', True)

    end = False
    if n < 0:
        data = _readOpeningPhrases()
        phrases = data['google_interposer']
        if TEST_FIX_GOOGLE_INTERPOSER is not None:
            response = phrases[TEST_FIX_GOOGLE_INTERPOSER]
        else:
            response = random.choice(phrases)
        noReply = False
    elif n >= 1000000:
        response = ' '
        noReply = True
        end = True
    else:
        if os.path.splitext(argFile)[1].lower() == '.py':
            with open(argFile, 'rt') as f:
                variables = {'n':n, 'accusationWords':accusationWords}
                exec(f.read(), variables)
                response = variables["response"]
                noReply = variables["last"]
        else:
            lines = _getTextLines(argFile)
            response = lines[n] if n < len(lines) else ' '
            noReply = (n >= len(lines)-1)
 
    if end:
        os.remove(argInfoFile)
    elif noReply:
        _setArgInfo(argFile, 1000000)
    else:
        _setArgInfo(argFile, n + 1)
            
    return (response, noReply)

def stopArgument():
    """
    Stop an argument part way through.
    
    Releases the lock. Any further calls to getNextResponse() will return a blank
    response ('') with noReply set.
    """
    initArguer()


# ---------------------------------------------------------------------------------------
# Main code - performs basic test of module

if __name__ == '__main__':
    initArguer()
    argFiles = (_getListOfArgFiles())
    for i,argFile in enumerate(argFiles):
        print('***', argFile)
        print('"' + startArgument('alexa', i) + '"')
        noReply = False
        noReply2 = False
        while not noReply2:
            noReply2 = noReply
            response, noReply = getNextResponse()
            print('"' + response + '"', noReply)
