
import sys
import Queue
import datetime
import time
import argparse

import twitterprocessor
import facebookprocessor
import nytprocessor
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
        self.keywords = set(keywords)
        self.dev_mode = dev_mode
        self.metrics = {'qlength':0, 'num_msg':0, 'throughput':0.0, 'latency':0.0 } 

        row = '\n'
        row += "Total # of msgs".rjust(20)
        row += "Throughput (msg/s)".rjust(20)
        row += "Queue Length (Msgs)".rjust(20)
        row += "Latency (s)".rjust(20)
        row += '\n'
        print row

    def launch(self):  
        t = twitterprocessor.TwitterProcessor(self.username, self.password, self.msg_queue, self.dev_mode)
        t.start()
        
        f = facebookprocessor.FacebookProcessor(self.msg_queue, self.dev_mode)
        f.start()
        
        nyt = nytprocessor.NYTProcessor(self.msg_queue, self.dev_mode)
        nyt.start()
        
        c = consumer.Consumer(self.msg_queue, self.keywords, self.update_metrics)
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

            row = str(self.metrics['num_msg']).rjust(20)
            row += "{0:.2f}".format(self.metrics['throughput']).rjust(20)
            row += str(self.metrics['qlength']).rjust(20)
            row += "{0:.2f}".format(self.metrics['latency']).rjust(20)
            print row

            time.sleep(0.5)

    def update_metrics(self, latency):
        self.metrics['num_msg'] += 1
        self.metrics['latency'] = latency


if __name__=="__main__":
    default_keywords = ['death', 'oil', 'party','boy', 'girl', 'tonight', 'fun', 'cool', 'interest', 'rate', 'climbing', 'people']
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', help='Please enter username for social accounts', default='ornitweet')
    parser.add_argument('-p', '--password', help='Please enter password for social accounts', default='ornithology')
    parser.add_argument('-d', '--dev', help='Please specify if DEV mode or not (default is PROD)', action='store_true')
    parser.add_argument('-k', '--keywords', nargs='+', help='Optional list of keywords with which to search social media', default=default_keywords)
    args = parser.parse_args()

    Supervisor(args.username, args.password, args.keywords, args.dev).launch()

