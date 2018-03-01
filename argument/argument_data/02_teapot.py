#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ******************************************************************************
# Argon Design Ltd. Project P9000 Argon
# (c) Copyright 2018 Argon Design Ltd. All rights reserved.
#
# Module : cyber_argument
# Author : Steve Barlow
# $Id: 02_teapot.py 22575 2018-03-01 14:28:56Z sjb $
# ******************************************************************************

"""
A simple "Yes I am!" / "No you aren't!" pantomime-style argument.

The argument starts with Alexa saying she is a teapot. Google says she is not. There is then
a "Yes I am!" / "No you aren't!" back and forth for 5 rounds. Finally Google says "This is
silly. No you aren't!" and Alexa does a last indignant "Oh yes, I am!".
"""

NTIMES = 5

# Input is the variables 'n' and 'accusationWords'
# Output must be 2 variables 'response' and 'last'
# n == 0, 2, 4 ... always corresponds to words that will said by Alexa
# The final response should have 'last' set

last = False

if n == 0:
    response = 'I\'m a teapot!'
elif n == 2 * NTIMES - 1:
    response = 'This is silly. No you\'re not!'
elif n == 2 * NTIMES:
    response = 'Oh yes, I am!'
    last = True
elif n % 2 == 0:
    response = 'Yes I am!'
else:
    response = 'No you\'re not!'
