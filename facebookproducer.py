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
            for json_file in content["data"]:
                msg = self.msg_dict(
                            source = 'facebook',
                            content = json_file['message'],
                            timestamp = self.parse_time(
                                            json_file['updated_time'],
                                            self.date_format),
                            msgID = json_file['id'],
                            authorID = json_file['from']['id'],
                            author = json_file['from']['name'],
                            color = 'blue'
                )
                self.msg_queue.put(msg)

            self.buffer = ""
            time.sleep(5)


    def write_function(self, data):
        """
        Callback for pycurl to write to buffer
        """
        self.buffer += data

