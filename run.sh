#!/bin/bash

export PATH="/home/sid/.local/bin:${PATH}"

#Migration
[[ ! -d "migrations" ]] && flask db init
[[ ! -f "migrations/alembic.ini" ]] && flask db init

flask db migrate
flask db upgrade

#Start Service
gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 --bind $HOST:5000 wsgi:app
