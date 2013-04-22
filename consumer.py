"""
Consumer processes all incoming messages
and searches for keywords
"""
import datetime
import socket
import json

import message

class Consumer(object):
    """
    Consumer that searches keywords for all messages
    """
    def __init__(self, msg_queue, update_metrics, dev_mode):
        
        self.alive = True
        self.msg_queue = msg_queue
        self.update_metrics_callback = update_metrics
        self.dev_mode = dev_mode
        self.word_to_clients = {}
        self.client_to_words = {}
        
        if not self.dev_mode:
            self.log_file = open('logs/log.json', 'a')

    def run(self):
        """
        Run method for thread that begins consumer process
        """
        while self.alive:
            msg = self.msg_queue.get(True)
            if msg.type == 'media':
                self.process_msg(msg)
            elif msg.type == 'connection':
                if msg.client in self.client_to_words:
                    for word in self.client_to_words.get[msg.client]:
                        self.word_to_clients[word].remove(msg.client)
                for word in msg.keywords:
                    if word in self.word_to_clients:
                        self.word_to_clients[word].append(msg.client) 
                    else:
                        self.word_to_clients[word] = [msg.client]
                self.client_to_words[msg.client] = msg.keywords
            elif msg.type == 'disconnection':
                for word in self.client_to_words[msg.client]:
                    self.word_to_clients[word].remove(msg.client)
                self.client_to_words.pop(msg.client)
            else: # msg type must be shutdown
                self.alive = False
                if not self.dev_mode:
                    self.log_file.flush()
                    self.log_file.close()

    def process_msg(self, msg):
        """
        Do the work needed on every single message
        """
        recipients = {}
        for word in set(msg.content.lower().split()):
            for client in self.word_to_clients.get(word, []):
                if client in recipients:
                    recipients[client].append(word)
                else:
                    recipients[client] = [word]

        for client in recipients:
            try:
                msg_dict = msg.to_dict()
                msg_dict['keywords'] = recipients[client]
                client.sendMessage(json.dumps(msg_dict), False)
            except socket.error:
                print "Disconnected client"
                pass

        latency = self.calculate_latency(msg.timestamp)
        self.update_metrics_callback(latency)

        if not self.dev_mode:
            self.log_file.write(msg.to_json() + '\n')

    @staticmethod
    def calculate_latency(msg_timestamp):
        """
        Calculates latency between current time and
        timestamp of the message
        """
        now = datetime.datetime.utcnow()
        delta = now - msg_timestamp
        return delta.total_seconds()
        
