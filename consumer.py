import threading
import Queue
import json
import datetime

COL1 = 10;
COL2 = 10;
COL3 = 40;
COL4 = 20;

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
                row += msg['source'].rjust(COL2)
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
        
