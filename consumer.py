"""
Consumer processes all incoming messages
and searches for keywords
"""
import datetime
import socket
#import time

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

        self.colors = {
            'red': '\033[31m',
            'green': '\033[32m',
            'yellow': '\033[33m',
            'blue': '\033[34m', 
            'purple': '\033[35m',
            'cyan': '\033[36m',
            'white': '\033[37m',
            'end': '\033[0m'
        }

    def run(self):
        """
        Run method for thread that begins consumer process
        """
        while self.alive:
            msg = self.msg_queue.get(True)
            if msg.type == 'media':
                self.process_msg(msg)
            elif msg.type == 'connection':
                self.client_to_words[msg.socket] = msg.keywords
                for word in msg.keywords:
                    if word in self.word_to_clients:
                        self.word_to_clients[word].append(msg.socket) 
                    else:
                        self.word_to_clients[word] = [msg.socket]
            elif msg.type == 'disconnection':
                for word in self.client_to_words[msg.socket]:
                    self.word_to_clients[word].remove(msg.socket)
                self.client_to_words.pop(msg.socket)
            else: # msg type must be shutdown
                self.alive = False
                self.log_file.flush()
                self.log_file.close()

    def process_msg(self, msg):
        """
        Do the work needed on every single message
        """
        recipients = {}
        for word in set(msg.content.lower().split()):
            for sock in self.word_to_clients.get(word, []):
                if sock in recipients:
                    recipients[sock].append(word)
                else:
                    recipients[sock] = [word]

        for sock in recipients:
            try:
                msg_dict = msg.to_dict()
                msg_dict['keywords'] = recipients[sock]
                sock.sendall(str(msg_dict))
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
        
