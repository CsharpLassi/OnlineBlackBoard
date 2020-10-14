#!/bin/bash

#Migration
[[ ! -d "migrations" ]] && flask db init
[[ ! -f "migrations/alembic.ini" ]] && flask db init

flask db migrate
flask db upgrade

#Start Service
gunicorn --worker-class eventlet -w 1 --bind $HOST:5000 wsgi:app