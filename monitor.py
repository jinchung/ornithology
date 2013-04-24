
"""
Monitor for application metrics
"""
import datetime
import json

from autobahn.websocket import WebSocketServerFactory
from autobahn.websocket import WebSocketServerProtocol

class MonitorServerProtocol(WebSocketServerProtocol):
    """
    Protocol for websocket connections with the Monitor Server
    """
    def onOpen(self):
        self.factory.register(self)

    def connectionLost(self, reason):
        WebSocketServerProtocol.connectionLost(self, reason)
        self.factory.unregister(self)

class MonitorServerFactory(WebSocketServerFactory):
    """
    Simple broadcast server broadcasting metrics to all
    currently connected admins.
    """

    def __init__(self, url, debug = False, debugCodePaths = False):
        WebSocketServerFactory.__init__(self, url, debug = debug, 
                                        debugCodePaths = debugCodePaths)
        self.qlength = 0
        self.num_msg = 0
        self.throughput = 0.0
        self.latency = 0.0
        self.num_clients = 0
   
        self.old_timestamp = datetime.datetime.utcnow()
        self.old_num_msg = 0

        self.clients = []

    def register(self, client):
        """
        Registering new web socket connections
        """
        if not client in self.clients:
            print "registered client " + client.peerstr
            self.clients.append(client)

    def unregister(self, client):
        """
        Unregistering existing web socket connections
        """
        if client in self.clients:
            print "unregistered client " + client.peerstr
            self.clients.remove(client)

    def broadcast(self):
        """
        Broadcasting metrics data
        """
        msg = json.dumps(self.metrics_dict())
        for client in self.clients:
            client.sendMessage(msg)

    def metrics_dict(self):
        """
        Put relevant metrics data of class into dict
        """
        return {"num_msgs" : self.num_msg,
                "throughput" : self.throughput, 
                "queue_lenght" : self.qlength,
                "latency" : self.latency,
                "num_clients" : self.num_clients}

    def update(self, qsize):
        """
        Start monitoring of system metrics
        """
        self.qlength = qsize
        
        now = datetime.datetime.utcnow()
        time_delta = now - self.old_timestamp
        num_msg_delta = self.num_msg - self.old_num_msg
        self.throughput = (num_msg_delta / time_delta.total_seconds())
        self.old_timestamp = now
        self.old_num_msg = self.num_msg

    def inc_clients(self):
        """
        Client count incrementor
        """
        self.num_clients += 1

    def dec_clients(self):
        """
        Client count decrementor
        """
        self.num_clients -= 1
     
    def metrics_callback(self, latency):
        """
        Callback to consumer to update metrics
        """
        self.num_msg += 1
        self.latency = latency

    def clean_exit(self):
        """
        Close all web socket connections on exit
        """
        for client in self.clients:
            client.connectionLost("Server shutting down")


