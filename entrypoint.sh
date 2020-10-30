#!/bin/sh

chown -R sip:sip /app/migrations
exec runuser -u sip "$@"
