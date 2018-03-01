#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ******************************************************************************
# Argon Design Ltd. Project P9000 Argon
# (c) Copyright 2018 Argon Design Ltd. All rights reserved.
#
# Module : cyber_argument
# Author : Steve Barlow
# $Id: 01_did_didnt.py 22575 2018-03-01 14:28:56Z sjb $
# ******************************************************************************

"""
A simple "No I didn't!" / "Yes you did!" pantomime-style argument.
"""

# Input is the variables 'n' and 'accusationWords'
# Output must be 2 variables 'response' and 'last'
# n == 0, 2, 4 ... always corresponds to words that will said by Alexa
# The final response should have 'last' set

if n == 0:
    response = 'You broke my home assistant and now it keeps repeating itself.'
elif n % 2 == 1:
    response = 'No I didn\'t!'
else:
    response = 'Yes you did!'

last = (n >= 10)
