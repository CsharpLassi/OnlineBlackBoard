#!/bin/bash

#Migration
[[ ! -d "migrations" ]] && flask db init
[[ ! -f "migrations/alembic.ini" ]] && flask db init

flask db migrate
flask db upgrade

#Start Service
gunicorn --worker-class eventlet --bind $HOST:5000 --workers=16 wsgi:app