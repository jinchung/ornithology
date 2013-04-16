"""
Consumer processes all incoming messages
and searches for keywords
"""
import datetime
#import time

import message

COL1 = 10
COL2 = 15
COL3 = 30
COL4 = 15

class Consumer(object):
    """
    Consumer that searches keywords for all messages
    """
    def __init__(self, msg_queue, update_metrics, dev_mode):
        
        self.alive = True
        self.msg_queue = msg_queue
        self.update_metrics_callback = update_metrics
        self.pretty_file = open('logs/pretty_log.txt', 'w')
        self.dev_mode = dev_mode
        self.word_map = {}
        
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
               for word in msg.keywords:
                    if word in self.word_map:
                        self.word_map[word].append(msg.socket) 
                    else:
                        self.word_map[word] = [msg.socket]
            else: # msg type must be shutdown
                self.alive = False
                self.pretty_file.flush()
                self.pretty_file.close()
                self.log_file.flush()
                self.log_file.close()

    def process_msg(self, msg):
        """
        Do the work needed on every single message
        """
        #time.sleep(0.01)
        for word in msg.content.lower().split():
            for sock in self.word_map.get(word, []):
                sock.sendall(msg.to_json())

        #self.pretty_print(matches, msg)
        latency = self.calculate_latency(msg.timestamp)
        self.update_metrics_callback(latency)

        if not self.dev_mode:
            self.log_file.write(msg.to_json() + '\n')

    def pretty_print(self, matches, msg):
        """
        Format each match and print them to pretty file
        """
        for match in matches:
            row = match.rjust(COL1)
            row += (self.colors[msg.color] +
                        msg.source.rjust(COL2) + self.colors['end'])
            row += str(msg.timestamp).rjust(COL3)
            row += str(msg.location).rjust(COL4)
            row += '\n'
            self.pretty_file.write(row)
            self.pretty_file.flush()

    @staticmethod
    def calculate_latency(msg_timestamp):
        """
        Calculates latency between current time and
        timestamp of the message
        """
        now = datetime.datetime.utcnow()
        delta = now - msg_timestamp
        return delta.total_seconds()
        
