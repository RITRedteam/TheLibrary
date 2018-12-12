from flask import abort, send_file

import os
import time

class Link():
    def __init__(self, filename, clicks, timeout):
        self.filename = filename
        self.clicks = int(clicks)
        if float(timeout) == 0.0:
            self.timeout = 0.0
        else:
            self.timeout = time.time() + float(timeout)

    def send_file(self):
        if self.clicks < 1 or self.timeout < time.time():
            if self.timeout != 0.0:
                return abort(404)
        self.clicks -= 1
        return send_file('files/'+self.filename)

    def __str__(self):
        return f"File: {self.filename}, Clicks: {self.clicks}, Timeout: {time.ctime(self.timeout)}"
