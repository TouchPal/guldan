import time
from werkzeug.serving import BaseRequestHandler


class GuldanRequestHandler(BaseRequestHandler):
    def handle(self):
        self.request_started = time.time()
        rv = super(GuldanRequestHandler, self).handle()
        return rv

    def send_response(self, *args, **kw):
        self.request_ended = time.time()
        super(GuldanRequestHandler, self).send_response(*args, **kw)

    def log_request(self, code='-', size='-'):
        duration = int((self.request_ended - self.request_started) * 1000)
        self.log('info', '"{0}" {1} {2} {3}ms'.format(self.requestline, code, size, duration))