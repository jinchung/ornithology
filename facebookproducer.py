"""
Producer for Facebook status updates
"""
import json
import pycurl
import time

import producer
import message

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
            json_content = json.loads(self.buffer)
            self.parse(json_content)

            self.buffer = ""
            time.sleep(5)

    def parse(self, json_content):
        """
        Parse the content of the API's json response
        into our predefined msg format
        """
        for json_file in json_content["data"]:
            msg = message.Message(
                        source = 'facebook',
                        content = json_file['message'],
                        timestamp = self.parse_time(
                                        json_file['updated_time'],
                                        self.date_format),
                        msg_id = json_file['id'],
                        author_id = json_file['from']['id'],
                        author = json_file['from']['name'],
                        color = 'blue'
            )
            self.msg_queue.put(msg)

    def write_function(self, data):
        """
        Callback for pycurl to write to buffer
        """
        self.buffer += data

