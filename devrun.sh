#!/bin/sh
export FLASK_APP=app.py
export FLASK_ENV='development'
export FLASK_RUN_HOST='localhost'
export FLASK_RUN_PORT=5000
flask run