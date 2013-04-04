
import datetime
import json
import pycurl
import time

import processor

class FacebookProcessor(processor.Processor):

    def __init__(self, msg_queue, dev_mode):
        super(FacebookProcessor, self).__init__(msg_queue, dev_mode)

        self.attributes = ['message', 'updated_time']
        self.date_format = '%Y-%m-%dT%H:%M:%S+0000'

        if not self.dev_mode:
            self.buffer = ""
            self.stream_url = 'https://graph.facebook.com/search?q=*&type=post'
            self.conn = pycurl.Curl()
            self.conn.setopt(pycurl.URL, self.stream_url)
            self.conn.setopt(pycurl.WRITEFUNCTION, self.write_function)

    def run(self):
        while True:
            self.conn.perform()
            content = json.loads(self.buffer)
            for msg in content["data"]:
                self.msg_queue.put(self.map(msg))
            self.buffer = ""
            time.sleep(5)

    def write_function(self, data):
        self.buffer += data

    def map(self, msg):
        msg = {key:value for (key,value) in msg.items() if key in self.attributes}
        result = {'source': 'facebook', 'content':msg['message'], 'location':None}
        result['timestamp'] = datetime.datetime.strptime(msg['updated_time'], self.date_format)
        return result


