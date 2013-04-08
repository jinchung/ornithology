"""
Spawn the twitter stream producer thread
Set up queue
Spawn consumer thread

Development Twitter account is:
Username: ornitweet
Password: ornithology
"""

import Queue
import datetime
import time
import argparse

import twitterprocessor
import facebookprocessor
import nytprocessor
import consumer

class Supervisor(object):
    """
    Supervisor class
    """
    def __init__(self, username, password, keywords):

        self.username = username
        self.password = password
        self.msg_queue = Queue.Queue()
        self.keywords = set(keywords)
        self.metrics = {
                'qlength':0,
                'num_msg':0,
                'throughput':0.0,
                'latency':0.0
        } 

        row = '\n'
        row += "Total # of msgs".rjust(20)
        row += "Throughput (msg/s)".rjust(20)
        row += "Queue Length (Msgs)".rjust(20)
        row += "Latency (s)".rjust(20)
        row += '\n'
        print row

    def launch(self):  
        """
        Launch whole application, producers and consumer
        """
        twitter = twitterprocessor.TwitterProcessor(self.username,
                                                    self.password,
                                                    self.msg_queue)
        twitter.start()
        
        facebook = facebookprocessor.FacebookProcessor(self.msg_queue)
        facebook.start()
        
        nyt = nytprocessor.NYTProcessor(self.msg_queue)
        nyt.start()
        
        con = consumer.Consumer(self.msg_queue, self.keywords,
                                self.update_metrics)
        con.start()
        
        old_timestamp = datetime.datetime.utcnow()
        old_num_msg = 0
        while True:
            self.metrics['qlength'] = self.msg_queue.qsize()
            
            now = datetime.datetime.utcnow()
            time_delta = now - old_timestamp
            num_msg_delta = self.metrics['num_msg'] - old_num_msg
            self.metrics['throughput'] = (num_msg_delta /
                                          time_delta.total_seconds())
            old_timestamp = now
            old_num_msg = self.metrics['num_msg']

            row = str(self.metrics['num_msg']).rjust(20)
            row += "{0:.2f}".format(self.metrics['throughput']).rjust(20)
            row += str(self.metrics['qlength']).rjust(20)
            row += "{0:.2f}".format(self.metrics['latency']).rjust(20)
            print row

            time.sleep(0.5)

    def update_metrics(self, latency):
        """
        Callback to consumer to update metrics
        """
        self.metrics['num_msg'] += 1
        self.metrics['latency'] = latency


if __name__ == "__main__":
    DEFAULT_KEYWORDS = [
            'death',
            'oil',
            'party',
            'boy',
            'girl',
            'tonight',
            'fun',
            'cool',
            'interest',
            'rate',
            'climbing',
            'people'
    ]
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument('-u', '--username',
                        help='Please enter username for social accounts',
                        default='ornitweet')

    PARSER.add_argument('-p', '--password',
                        help='Please enter password for social accounts',
                        default='ornithology')

    PARSER.add_argument('-k', '--keywords', nargs='+',
                        help="Optional list of keywords with"
                             "which to search social media",
                        default=DEFAULT_KEYWORDS)

    ARGS = PARSER.parse_args()

    Supervisor(ARGS.username, ARGS.password, ARGS.keywords).launch()

