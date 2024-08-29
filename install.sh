#!/bin/sh

# Prevent command with Service Token being recorded in bash history
# export DOPPLER_TOKEN='dp.st.prd.xxxx'

export HISTIGNORE='export DOPPLER_TOKEN*'

pip3 install --no-cache-dir -r requirements.txt