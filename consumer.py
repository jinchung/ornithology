"""
Consumer processes all incoming messages
and searches for keywords
"""
import threading
import datetime
import time

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
        self.logfile = open('matched_msgs.log', 'w')
        self.end = '\033[0m'

    def run(self):
        while True:
            msg = self.msg_queue.get(True)
            time.sleep(0.01)
            text = set(msg['content'].lower().split())
            matches = self.keywords.intersection(text)
            for match in matches:
                row = match.rjust(COL1)
                row += msg['color'] + msg['source'].rjust(COL2) + self.end
                row += str(msg['timestamp']).rjust(COL3)
                row += str(msg['location']).rjust(COL4)
                row += '\n'
                self.logfile.write(row)
                self.logfile.flush()
            latency = self.calculate_latency(msg['timestamp'])
            self.update_metrics_callback(latency)

    @staticmethod
    def calculate_latency(msg_timestamp):
        """
        Calculates latency between current time and
        timestamp of the message
        """
        now = datetime.datetime.utcnow()
        delta = now - msg_timestamp
        return delta.total_seconds()
        
