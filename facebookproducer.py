"""
Producer for Facebook status updates
"""
import json
import pycurl
import time

import producer

class FacebookProducer(producer.Producer):
    """
    Facebook Producer thread for gathering status updates
    """
    def __init__(self, msg_queue):
        super(FacebookProducer, self).__init__(msg_queue)

        self.attributes = [
                              'message',
                              'updated_time',
                              'id',
                              'from.name',
                              'from.id'
                          ]

        self.date_format = '%Y-%m-%dT%H:%M:%S'

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
        """
        Callback for pycurl to write to buffer
        """
        self.buffer += data

    def map(self, msg):
        msg = {key:value for (key, value) in msg.items() 
               if key in self.attributes}
        # above will not be able to extract user info

        source = 'facebook'
        #authorID = msg['']
        #author
        #msgID
        color = self.colors['blue']
        content = msg['message']
        location = None
        timestamp = self.parse_time(msg['updated_time'], self.date_format)

        return self.map_to_std_msg(source, authorID, author, msgID, color,
                                   content, location, timestamp)



