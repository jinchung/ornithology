"""
Consumer processes all incoming messages
and searches for keywords
"""
import os.path
import datetime
import socket
import json
import collections

class Consumer(object):
    """
    Consumer that searches keywords for all messages
    """
    def __init__(self, msg_queue, update_metrics, dev_mode, archiving):
        
        self.alive = True
        self.msg_queue = msg_queue
        self.update_metrics_callback = update_metrics
        self.dev_mode = dev_mode
        self.archiving = archiving
        self.word_to_clients = collections.defaultdict(lambda: list())
        self.client_to_words = collections.defaultdict(lambda: list())

        if not self.dev_mode and self.archiving:
            base, _ = os.path.split(os.path.dirname(__file__))
            log_file = os.path.join(base, "logs", "log.json")
            self.log_file = open(log_file, 'a')

    def run(self):
        """
        Run method for thread that begins consumer process
        """
        while self.alive:
            msg = self.msg_queue.get(True)
            if msg.type == 'media':
                self.process_msg(msg)
            elif msg.type == 'connection':
                self.process_connection(msg)
            elif msg.type == 'disconnection':
                self.process_disconnection(msg)
            else: # msg type must be shutdown
                self.process_shutdown()

    def process_msg(self, msg):
        """
        Do the work needed on every single message
        """
        recipients = collections.defaultdict(lambda: list())
        for word in set(msg.content.lower().split()):
            for client in self.word_to_clients.get(word, []):
                recipients[client].append(word)

        for client in recipients:
            msg_dict = msg.to_dict()
            msg_dict['keywords'] = recipients[client]
            try:
                client.sendMessage(json.dumps(msg_dict), False)
            except socket.error:
                print "User got disconnected"

        latency = self.calculate_latency(msg.timestamp)
        self.update_metrics_callback(latency)

        if not self.dev_mode and self.archiving:
            self.log_file.write(msg.to_json() + '\n')

    def process_connection(self, msg):
        """
        handles a new connection
        """

        self.process_disconnection(msg) # clean slate, janitoring

        for word in msg.keywords:
            self.word_to_clients[word].append(msg.client) 

        self.client_to_words[msg.client] = msg.keywords

    def process_disconnection(self, msg):
        """
        handles a disconnection
        """
        if msg.client in self.client_to_words:
            for word in self.client_to_words[msg.client]:
                self.word_to_clients[word].remove(msg.client)
            self.client_to_words.pop(msg.client)

    def process_shutdown(self):
        """
        handles a shutdown message
        """

        self.alive = False

        for client in self.client_to_words:
            client.connectionLost("Server shutting down")

        if not self.dev_mode and self.archiving:
            self.log_file.flush()
            self.log_file.close()

    @staticmethod
    def calculate_latency(msg_timestamp):
        """
        Calculates latency between current time and
        timestamp of the message
        """
        now = datetime.datetime.utcnow()
        delta = now - msg_timestamp
        return delta.total_seconds()
        
