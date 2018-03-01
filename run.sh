#!/bin/bash
# ******************************************************************************
# Argon Design Ltd. Project P9000 Argon
# (c) Copyright 2018 Argon Design Ltd. All rights reserved.
#
# Module : cyber_argument
# Author : Steve Barlow
# $Id: run.sh 22575 2018-03-01 14:28:56Z sjb $
# ******************************************************************************

# run.sh - Start local server

# Opens a tabbed terminal window with 3 tabs - one for the alexa server, one for the google server and one for ngrok
gnome-terminal \
    --tab --title cyberarg_alexa -e cyberarg_alexa/cyberarg_alexa.py \
    --tab --title cyberarg_google -e cyberarg_google/cyberarg_google.py \
    --tab --title ngrok -x ngrok start -config ~/.ngrok2/ngrok.yml -config ngrok.yml cyberarg_alexa cyberarg_google
