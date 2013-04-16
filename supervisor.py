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
import signal
import sys
import socket
import select

import twitterproducer
import facebookproducer
import nytproducer
import consumer
import replayproducer
import message


class Supervisor(object):
    """
    Supervisor class
    """
    def __init__(self, config, dev_mode):
        self.alive = True
        self.config = config
        self.dev_mode = dev_mode
        self.msg_queue = Queue.Queue(maxsize=200)
        self.producers = []
        self.metrics = {
                'qlength':0,
                'num_msg':0,
                'throughput':0.0,
                'latency':0.0
        } 

        host = self.config['Socket']['host']
        port = int(self.config['Socket']['port'])
        self.listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listen_sock.bind((host, port))
        self.listen_sock.listen(100)

        self.old_timestamp = datetime.datetime.utcnow()
        self.old_num_msg = 0
        
        row = '\n'
        row += "Total # of msgs".rjust(20)
        row += "Throughput (msg/s)".rjust(20)
        row += "Queue Length (Msgs)".rjust(20)
        row += "Latency (s)".rjust(20)
        row += '\n'
        print row

    def generate_producers(self):
        """
        Generate all producer objects
        """
        if self.dev_mode:
            self.producers.append(replayproducer.ReplayProducer(self.msg_queue))
        else: 
            self.producers.append(twitterproducer.TwitterProducer(
                            self.config['Twitter']['username'],
                            self.config['Twitter']['password'],
                            self.msg_queue))
            
            self.producers.append(
                            facebookproducer.FacebookProducer(self.msg_queue))
            
            self.producers.append(nytproducer.NYTProducer(
                            self.config['NYT']['api_key'],
                            self.msg_queue))

    def consumers(self):
        """
        Generator that launches consumer(s)
        """
        yield consumer.Consumer(self.msg_queue, 
                                self.update_metrics, self.dev_mode)
        
    def launch(self):  
        """
        Launch whole application: producers,consumer, system monitoring
        """
        self.generate_producers()
        for producer in self.producers:
            thread = threading.Thread(target=producer.run)
            thread.start()

        for consumer_ in self.consumers():
            thread = threading.Thread(target=consumer_.run)
            thread.start()

        self.supervise()

    def supervise(self):
        while self.alive:
            self.monitor_system()
            self.loop(1)
    
    def monitor_system(self):
        """
        Start monitoring of system metrics
        """
        self.metrics['qlength'] = self.msg_queue.qsize()
        
        now = datetime.datetime.utcnow()
        time_delta = now - self.old_timestamp
        num_msg_delta = self.metrics['num_msg'] - self.old_num_msg
        self.metrics['throughput'] = (num_msg_delta /
                                      time_delta.total_seconds())
        self.old_timestamp = now
        self.old_num_msg = self.metrics['num_msg']

        self.print_metrics()

    def loop(self, timeout):
        readable_socket, _, _ = select.select([self.listen_sock], 
                                              [], [], timeout)

        for sock in readable_socket:
            client_sock, _ = self.listen_sock.accept()
            request = client_sock.recv(1028)
            keywords = request.split() 
            connMsg = message.ConnectionMessage(client_sock, keywords)
            self.msg_queue.put(connMsg) 

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

    def clean_exit(self, *unused):
        """
        Clean exit that kills all producer and consumer threads
        """
        print 'Received exit signal. Please wait for cleanup...'
        self.alive = False
        for producer in self.producers:
            producer.stop()
        self.msg_queue.put(message.ShutdownSignal()) 
        sys.exit(0)

def parse_args():
    """
    Argument setup and parsing
    """
    parser = argparse.ArgumentParser()
   
    parser.add_argument('-d', '--dev',
                        help='Specify dev mode or not (default is PROD)',
                        action='store_true')

    return parser.parse_args()

def get_config():
    """
    Retrieve and parse system config file
    """
    config = ConfigParser.RawConfigParser()
    config.read('ornithology.cfg')
    return {section:dict(config.items(section)) 
            for section in config.sections()}

if __name__ == "__main__":
    ARGS = parse_args()
    CONFIG = get_config()
    SUPER = Supervisor(CONFIG, ARGS.dev)
    signal.signal(signal.SIGINT, SUPER.clean_exit)
    SUPER.launch()
