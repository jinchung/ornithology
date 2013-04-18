"""
Replay processor that reads logs to replay messages
"""
import json
import datetime

import producer
import message

class ReplayProducer(producer.Producer):
    """
    Replay producer for logs
    """

    def __init__(self, msg_queue):
        super(ReplayProducer, self).__init__(msg_queue)
        self.date_format = '%Y-%m-%d %H:%M:%S'

    def run(self): 
        logfile = open('logs/log.json', 'r')
        for line in logfile:
            try:
                msg = json.loads(line)
            except ValueError:
                continue
            msg['timestamp'] = datetime.datetime.strptime(msg['timestamp'], 
                                                          self.date_format) 
            self.msg_queue.put(message.MediaMessage(**msg))

