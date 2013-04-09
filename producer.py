"""
Base class for producers that put content on the queue
"""

import threading
import abc
import re
import datetime

class Producer(threading.Thread):
    """
    Base class for producers that put content on the queue
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, msg_queue):
        threading.Thread.__init__(self)
        self.msg_queue = msg_queue
        self.colors = {
            'red': '\033[31m',
            'green': '\033[32m',
            'yellow': '\033[33m',
            'blue': '\033[34m', 
            'purple': '\033[35m',
            'cyan': '\033[36m',
            'white': '\033[37m',
        }

    @abc.abstractmethod
    def run(self):
        return

    @staticmethod
    def parse_time(timestr, fmt):
        """
        Custom time parsing function because datetime.datetime.strptime()
        didn't handle UTC offset %z well
        """

        regex = r'[+-][01]\d:?\d\d'
        offset = re.findall(regex, timestr)
        if offset:
            hours = int(offset[0][:3])
            mins = int(offset[0][-2:])
            delta = datetime.timedelta(hours=hours, minutes=mins) 
            timestr = timestr.replace(offset[0], '')
        else:
            delta = datetime.timedelta()
        date = datetime.datetime.strptime(timestr, fmt)
        return date + delta

    def map_to_std_msg(self, source, authorID, author, msgID, color,
            content, location, timestamp):
        """
        Map 
        each key of interest to
        global msg keys
        """
        result = {
                    'source': source, 
                    'authorID': authorID,
                    'author': author,
                    'msgID': msgID,
                    'color': color, 
                    'content': content, 
                    'location': location,
                    'timestamp': timestamp
        }
        return result

