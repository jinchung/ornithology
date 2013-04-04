
import sys
import Queue
import datetime
import time

import twitterprocessor
import facebookprocessor
import consumer

"""
Spawn the twitter stream producer thread
Set up queue
Spawn consumer thread

Usage:
    $ python supervisor.py uSErName pa$$w0rd

    or

    $ python supervisor.py -D uSErName pa$$w0rd # for turning dev mode on


Development Twitter account is:
Username: ornitweet
Password: ornithology
"""

class Supervisor(object):
    def __init__(self, username, password, keywords, dev_mode):
        self.username = username
        self.password = password
        self.msg_queue = Queue.Queue()
        self.keywords = keywords
        self.dev_mode = dev_mode
        self.metrics = {'qlength':0, 'num_msg':0, 'throughput':None, 'latency':None } 

    def launch(self):  
        t = twitterprocessor.TwitterProcessor(self.username, self.password, self.msg_queue, self.dev_mode)
        f = facebookprocessor.FacebookProcessor(self.msg_queue, self.dev_mode)
        c = consumer.Consumer(self.msg_queue, self.keywords, self.update_metrics)
        t.start()
        f.start()
        c.start()
        old_timestamp = datetime.datetime.utcnow()
        old_num_msg = 0
        while True:
            self.metrics['qlength'] = self.msg_queue.qsize()
            
            now = datetime.datetime.utcnow()
            time_delta = now - old_timestamp
            num_msg_delta = self.metrics['num_msg'] - old_num_msg
            self.metrics['throughput'] = num_msg_delta / time_delta.total_seconds()
            old_timestamp = now
            old_num_msg = self.metrics['num_msg']

            print self.metrics
            time.sleep(0.5)

    def update_metrics(self, latency):
        self.metrics['num_msg'] += 1
        self.metrics['latency'] = latency


if __name__=="__main__":
    if len(sys.argv) == 3:
        _, username, password = sys.argv
        dev_mode = False
    elif len(sys.argv) == 4 and sys.argv[1] in ["-d","-D"]:
        _, dev_mode, username, password = sys.argv
        dev_mode = True
    else:
        print(supervisor.__doc__)

    print("Please enter the keywords you want to monitor, separated by commas, and press enter: ")
    keywords = sys.stdin.readline()
    keywords = {word.strip() for word in keywords.split(',')}

    Supervisor(username, password, keywords, dev_mode).launch()

