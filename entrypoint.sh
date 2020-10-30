#!/bin/sh

chown -R sid:sid /app/migrations
su sid
exec "$@"
