#!/usr/bin/python
from onlineblackboard import create_app
from werkzeug.middleware.proxy_fix import ProxyFix

from OnlineBlackBoard.onlineblackboard.ext import socket

app = create_app()
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)
