#!/bin/sh
export FLASK_APP=app.py
export FLASK_ENV='development'
export FLASK_RUN_HOST=$(ip -4 addr show wlan0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}')
export FLASK_RUN_PORT=8000
flask run
