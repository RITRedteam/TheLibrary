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
    
    def validate(self):
        """Validate that the link is still working
        The following links are removed:
            - Links for files that have been deleted
            - Links that have timed out
            - Links that have been clicked too many times
        
        Returns:
            bool: Whether or not the link is still valid
        """
        if self.timeout < time.time() and self.timeout != 0.0:
            return False # Return false is there is an expiration time and it has expired
        if self.clicks < 1:
            return False # Return false is the # of clicks has passed
        
        # If the file is still there, its a valid link
        return os.path.isfile('files/'+self.filename)


