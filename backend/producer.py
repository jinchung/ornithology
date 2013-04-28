"""
Base class for producers that put content on the queue
"""

import abc
import re
import datetime

class Producer(object):

    """
    Base class for producers that put content on the queue
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, msg_queue):
        self.msg_queue = msg_queue
        self.alive = True

    def stop(self):
        """
        Sets alive status to False in order to stop producer threads
        """
        self.alive = False

    @abc.abstractmethod
    def run(self):
        """
        Abstract method implemented by producers for thread to run
        """
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

