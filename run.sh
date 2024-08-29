#!/bin/sh

doppler run --command='gunicorn -w 3 -b 0.0.0.0:$PORT server:app'