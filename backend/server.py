
"""
Spawn the twitter stream producer thread
Set up queue
Spawn consumer thread

Development Twitter account is:
Username: ornitweet
Password: ornithology
"""

import Queue
import threading

from autobahn.websocket import WebSocketServerProtocol
from autobahn.websocket import WebSocketServerFactory 

import twitterproducer
import facebookproducer
import nytproducer
import consumer
import replayproducer
import message

class ServerProtocol(WebSocketServerProtocol):
    """
    Client protocol for the websockets
    """

    def init(self):
        print "in server protocol: got connection"
        super(ServerProtocol, self).__init__()

    def onMessage(self, msg, binary):
        print "in server protocol: got msg"
        self.factory.register(self, msg)

    def connectionLost(self, reason):
        WebSocketServerProtocol.connectionLost(self, reason)
        self.factory.unregister(self)

class ServerFactory(WebSocketServerFactory):
    """
    Factory for websockets clients.
    """
    def __init__(self, url, monitor, config, dev_mode,
                 debug = False, debugCodePaths = False):
        WebSocketServerFactory.__init__(self, url, debug = debug,
                                        debugCodePaths = debugCodePaths)
        self.config = config
        self.dev_mode = dev_mode
        self.msg_queue = Queue.Queue(maxsize=200)
        self.producers = []
        self.monitor = monitor
        print "in server: properly exiting server factory constructor... "

    def register(self, client, msg):
        """
        register a new client
        """
        keywords = msg.lower().split() 
        conn_msg = message.ConnectionMessage(client, keywords)
        self.msg_queue.put(conn_msg) 
        self.monitor.inc_clients()
        print "New user! (or existing user changed keywords) ",
        print client.peerstr

    def unregister(self, client):
        """
        unregister a client
        """
        disconn_msg = message.DisconnectionMessage(client)
        self.msg_queue.put(disconn_msg) 
        self.monitor.dec_clients()
        print "User " + client.peerstr + " left\n"

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
            print "in server factory: producers generated... "

    def consumers(self):
        """
        Generator that launches consumer(s)
        """
        yield consumer.Consumer(self.msg_queue, 
                                self.monitor.metrics_callback,
                                self.dev_mode,
                                self.config['Configs']['archiving'].lower()=='true')
        
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
        """
        function that is called periodically
        from the twisted reactor to update
        system metric
        """
        self.monitor.update(self.msg_queue.qsize())
        self.monitor.broadcast()
        
    def clean_exit(self, *unused):
        """
        Clean exit that kills all producer and consumer threads
        """
        del unused
        print 'Received exit signal. Please wait for cleanup...'
        for producer in self.producers:
            producer.stop()
        self.monitor.clean_exit()
        self.msg_queue.put(message.ShutdownSignal()) 

