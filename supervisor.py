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
import ConfigParser
import threading

import twitterproducer
import facebookproducer
import nytproducer
import consumer
import replayproducer



class Supervisor(object):
    """
    Supervisor class
    """
    def __init__(self, config, dev_mode, keywords):

        self.config = config
        self.dev_mode = dev_mode
        self.msg_queue = Queue.Queue(maxsize=200)
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

    def producers(self):
        # Launch every APIs
        if self.dev_mode:
            yield replayproducer.ReplayProducer(self.msg_queue)
            yield replayproducer.ReplayProducer(self.msg_queue)
            yield replayproducer.ReplayProducer(self.msg_queue)
        else: 
            yield twitterproducer.TwitterProducer(
                            self.config['Twitter']['username'],
                            self.config['Twitter']['password'],
                            self.msg_queue)
            
            yield facebookproducer.FacebookProducer(self.msg_queue)
            
            yield nytproducer.NYTProducer(
                            self.config['NYT']['api_key'],
                            self.msg_queue)

    def consumers(self):
        # Launch consumer
        yield consumer.Consumer(self.msg_queue, self.keywords,
                                self.update_metrics, self.dev_mode)
        
    def launch(self):  
        for producer in self.producers():
            thread = threading.Thread(target=producer.run)
            thread.start()

        for consumer in self.consumers():
            thread = threading.Thread(target=consumer.run)
            thread.start()

        """
        Launch whole application, producers and consumer
        """
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

            self.print_metrics()
            time.sleep(0.5)

    def print_metrics(self):
        """
        Pretty print metrics to shell
        """
        row = str(self.metrics['num_msg']).rjust(20)
        row += "{0:.2f}".format(self.metrics['throughput']).rjust(20)
        row += str(self.metrics['qlength']).rjust(20)
        row += "{0:.2f}".format(self.metrics['latency']).rjust(20)
        print row

    def update_metrics(self, latency):
        """
        Callback to consumer to update metrics
        """
        self.metrics['num_msg'] += 1
        self.metrics['latency'] = latency

def parse_args():
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
    parser = argparse.ArgumentParser()
   
    parser.add_argument('-d', '--dev',
                        help='Specify dev mode or not (default is PROD)',
                        action='store_true')

    parser.add_argument('-k', '--keywords', nargs='+',
                        help="Optional list of keywords with"
                             "which to search social media",
                        default=DEFAULT_KEYWORDS)

    return parser.parse_args()

def get_config():
    config = ConfigParser.RawConfigParser()
    config.read('ornithology.cfg')
    return {section:dict(config.items(section)) for section in config.sections()}

if __name__ == "__main__":
    ARGS = parse_args()
    CONFIG = get_config()
    Supervisor(CONFIG, ARGS.dev, ARGS.keywords).launch()

