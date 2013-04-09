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

    def msg_dict(self, source, content, timestamp, msgID=None,
                authorID=None, author=None, color='white', location=None):
        """
        Create a dictionary of msg format from its inputs
        """
        return  {
                    'source': source, 
                    'content': content, 
                    'timestamp': timestamp,
                    'msgID': msgID,
                    'authorID': authorID,
                    'author': author,
                    'color': color, 
                    'location': location
                }

