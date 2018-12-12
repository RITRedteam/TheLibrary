from flask import abort, send_file

import os
import time

class Link():
    def __init__(self, filename, clicks, timeout):
        self.filename = filename
        self.clicks = int(clicks)
        if float(timeout) == 0.0:
            timeout = 3600000.0 # 1000 Hours (no way the competition goes longer)
        self.timeout = time.time() + float(timeout)

    def send_file(self):
        if self.clicks < 1 or self.timeout < time.time():
            return abort(404)
        self.clicks -= 1
        return send_file('files/'+self.filename)
