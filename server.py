
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
import threading

from autobahn.websocket import WebSocketServerProtocol
from autobahn.websocket import WebSocketServerFactory 

import twitterproducer
import facebookproducer
import nytproducer
import consumer
import replayproducer
import message
import monitor

class ServerProtocol(WebSocketServerProtocol):

    def onMessage(self, msg, binary):
        self.factory.register(self, msg)

    def connectionLost(self, reason):
        WebSocketServerProtocol.connectionLost(self, reason)
        self.factory.unregister(self)

class ServerFactory(WebSocketServerFactory):

    def __init__(self, url, monitor, config, dev_mode, debug = False, debugCodePaths = False):
        WebSocketServerFactory.__init__(self, url, debug = debug, debugCodePaths = debugCodePaths)
        self.config = config
        self.dev_mode = dev_mode
        self.msg_queue = Queue.Queue(maxsize=200)
        self.producers = []
        self.monitor = monitor

    def register(self, client, msg):
        keywords = msg.lower().split() 
        connMsg = message.ConnectionMessage(client, keywords)
        self.msg_queue.put(connMsg) 
        self.monitor.inc_clients()
        print "New client! (or existing client changed keywords " + client.peerstr

    def unregister(self, client):
        disconnMsg = message.DisconnectionMessage(client)
        self.msg_queue.put(disconnMsg) 
        self.monitor.dec_clients()
        print "unregistered client " + client.peerstr

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
        
    def setup(self):  
        """
        Launch whole application: producers, consumer 
        """
        self.generate_producers()
        for producer in self.producers:
            thread = threading.Thread(target=producer.run)
            thread.start()

        for consumer_ in self.consumers():
            thread = threading.Thread(target=consumer_.run)
            thread.start()

    def monitor_callback(self):
        self.monitor.update(self.msg_queue.qsize())
        self.monitor.broadcast()
        
    def clean_exit(self, *unused):
        """
        Clean exit that kills all producer and consumer threads
        """
        print 'Received exit signal. Please wait for cleanup...'
        for producer in self.producers:
            producer.stop()
        self.monitor.clean_exit()
        self.msg_queue.put(message.ShutdownSignal()) 

