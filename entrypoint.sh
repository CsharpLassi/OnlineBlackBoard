#!/bin/sh

chown -R sid:sid /app/migrations
exec runuser --user sid "$@"
