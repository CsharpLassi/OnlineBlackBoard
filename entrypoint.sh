#!/bin/sh

mkdir -p /app/blackboard_data

chown -R sid:sid /app/migrations
chown -R sid:sid /app/blackboard_data

exec runuser -u sid "$@"
