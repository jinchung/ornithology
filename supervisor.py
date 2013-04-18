"""
Spawn the twitter stream producer thread
Set up queue
Spawn consumer thread

Development Twitter account is:
Username: ornitweet
Password: ornithology
"""

import Queue
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
import monitor

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
        self.monitor = monitor.Monitor()

        host = self.config['Socket']['host']
        port = int(self.config['Socket']['port'])
        self.listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listen_sock.bind((host, port))
        self.listen_sock.listen(100)

        self.client_sockets = []

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
                                self.monitor.metrics_callback, self.dev_mode)
        
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
            self.monitor.update(self.msg_queue.qsize())
            self.loop(1)
    
    def loop(self, timeout):
        all_sockets = self.client_sockets + [self.listen_sock]
        readable_sockets, _, _ = select.select(all_sockets, [], [], timeout)

        for sock in readable_sockets:
            if sock == self.listen_sock: # new connection
                client_sock, _ = sock.accept()
                request = client_sock.recv(1028)
                keywords = request.lower()..split() 
                connMsg = message.ConnectionMessage(client_sock, keywords)
                self.client_sockets.append(client_sock)
                self.monitor.inc_clients()
                self.msg_queue.put(connMsg) 
            else: # a client is telling us smtg
                print 'client is telling us something!'
                try:
                    request = sock.recv(1028)
                except socket.error:
                    request = None
                if not request: # a client disconnection
                    print 'client is disconnecting'
                    self.client_sockets.remove(sock)
                    disconnMsg = message.DisconnectionMessage(sock)
                    self.monitor.dec_clients()
                    self.msg_queue.put(disconnMsg) 

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
