"""
Consumer processes all incoming messages
and searches for keywords
"""
import threading
import datetime
import time
import json

COL1 = 10
COL2 = 15
COL3 = 30
COL4 = 15

class Consumer(threading.Thread):
    """
    Consumer thread that searches keywords for all messages
    """
    def __init__(self, msg_queue, keywords, update_metrics):
        threading.Thread.__init__(self)
        self.msg_queue = msg_queue
        self.keywords = keywords
        self.update_metrics_callback = update_metrics
        self.pretty_file = open('logs/pretty_log.txt', 'w')
        self.log_file = open('logs/log.json', 'a')

        self.colors = {
            'red': '\033[31m',
            'green': '\033[32m',
            'yellow': '\033[33m',
            'blue': '\033[34m', 
            'purple': '\033[35m',
            'cyan': '\033[36m',
            'white': '\033[37m',
            'end': '\033[0m'
        }

    def run(self):
        while True:
            msg = self.msg_queue.get(True)
            self.process_msg(msg)

    def process_msg(self, msg):
        """
        Do the work needed on every single message
        """
        time.sleep(0.01)
        text = set(msg['content'].lower().split())
        matches = self.keywords.intersection(text)
        self.pretty_print(matches, msg)
        latency = self.calculate_latency(msg['timestamp'])
        self.update_metrics_callback(latency)

        msg['timestamp'] = str(msg['timestamp'])
        self.log_file.write(json.dumps(msg))

    def pretty_print(self, matches, msg):
        """
        Format each match and print them to pretty file
        """
        for match in matches:
            row = match.rjust(COL1)
            row += (self.colors[msg['color']] +
                        msg['source'].rjust(COL2) + self.colors['end'])
            row += str(msg['timestamp']).rjust(COL3)
            row += str(msg['location']).rjust(COL4)
            row += '\n'
            self.pretty_file.write(row)
            self.pretty_file.flush()

    @staticmethod
    def calculate_latency(msg_timestamp):
        """
        Calculates latency between current time and
        timestamp of the message
        """
        now = datetime.datetime.utcnow()
        delta = now - msg_timestamp
        return delta.total_seconds()
        
