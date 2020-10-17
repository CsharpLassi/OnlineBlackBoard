#!/usr/bin/python
from onlineblackboard import create_app


class ReverseProxied(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        scheme = environ.get('HTTP_X_FORWARDED_PROTO')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)


app = create_app()
app.wsgi_app = ReverseProxied(app.wsgi_app)
