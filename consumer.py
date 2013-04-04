import threading
import Queue
import json
import datetime

BLUE = '\033[34m'
GREEN = '\033[32m'
END = '\033[0m'

COL1 = 10;
COL2 = 15;
COL3 = 30;
COL4 = 15;

class Consumer(threading.Thread):

    def __init__(self, msg_queue, keywords, update_metrics):
        threading.Thread.__init__(self)
        self.msg_queue = msg_queue
        self.keywords = keywords
        self.update_metrics_callback = update_metrics
        self.logfile = open('matched_msgs.log', 'w')

    def run(self):
        while True:
            msg = self.msg_queue.get(True)
            text = set(msg['content'].lower().split())
            matches = self.keywords.intersection(text)
            for match in matches:
                row = match.rjust(COL1)
                prefix = BLUE if msg['source'] == 'facebook' else GREEN
                row += prefix + msg['source'].rjust(COL2) + END
                row += str(msg['timestamp']).rjust(COL3)
                row += str(msg['location']).rjust(COL4)
                row += '\n'
                self.logfile.write(row)
                self.logfile.flush()

            self.update_metrics_callback(self.calculate_latency(msg['timestamp']))

    def calculate_latency(self, msg_timestamp):
        now = datetime.datetime.utcnow()
        delta = now - msg_timestamp
        return delta.total_seconds()
        
