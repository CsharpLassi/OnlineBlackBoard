#!/bin/bash

#Migration
[[ ! -d "migrations" ]] && flask db init
[[ ! -f "migrations/alembic.ini" ]] && flask db init

flask db migrate
flask db upgrade

#Start Service
cd src || exit
gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 --bind $HOST:5000 wsgi:app