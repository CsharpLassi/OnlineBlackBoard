#!/bin/bash

#Migration
[[ ! -d "migrations" ]] && flask db init
[[ ! -f "migrations/alembic.ini" ]] && flask db init

flask db migrate
flask db upgrade

#Start Service
gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker --bind $HOST:5000 --workers=4 wsgi:app