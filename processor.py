import threading
import Queue
import abc
import re
import datetime

class Processor(threading.Thread):
    __metaclass__ = abc.ABCMeta

    def __init__(self, msg_queue, dev_mode):
        threading.Thread.__init__(self)
        self.msg_queue = msg_queue
        self.dev_mode = dev_mode
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
    def parseTimezone(timestr, format):
        regex = r'[+-][01]\d:?\d\d'
        offset = re.findall(regex, timestr)
        if offset:
            hours = int(offset[0][:3])
            mins = int(offset[0][-2:])
            delta = datetime.timedelta(hours=hours, minutes=mins) 
            timestr = timestr.replace(offset[0], '')
        else:
            delta = datetime.timedelta()
        date = datetime.datetime.strptime(timestr, format)
        return date + delta
        

    @abc.abstractmethod
    def map(self, raw_msg):
        """
        takes a dictionary and map
        each key of interest to
        global msg keys
        """
        return

