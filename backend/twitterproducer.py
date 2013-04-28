"""
Twitter subclass for pulling content from Twitter API
"""

import pycurl
import json

import producer
import message

class TwitterProducer(producer.Producer):
    """
    Twitter subclass for pulling content from Twitter API
    """

    def __init__(self, username, password, msg_queue):
        super(TwitterProducer, self).__init__(msg_queue)
        self.date_format = '%a %b %d %H:%M:%S %Y'

        self.stream_url = 'https://stream.twitter.com/1.1/statuses/sample.json'
        self.username = username
        self.password = password
        self.buffer = ""
        self.conn = pycurl.Curl()
        self.conn.setopt(pycurl.USERPWD,
                         "%s:%s" % (self.username, self.password))
        self.conn.setopt(pycurl.URL, self.stream_url)
        self.conn.setopt(pycurl.WRITEFUNCTION, self.on_receive)
        self.conn.setopt(pycurl.NOSIGNAL, 1)

    def run(self):
        try:
            self.conn.perform()
        except pycurl.error:
            self.conn.close()

    def on_receive(self, data):
        """
        Behavior on the receival of content from Twitter
        """
        if self.alive:
            self.buffer += data
            json_file = json.loads(self.buffer)
            self.buffer = ""

            if 'text' in json_file.keys():
                msg = message.MediaMessage(
                                source = 'twitter',
                                content = json_file['text'],
                                timestamp = self.parse_time(
                                                json_file['created_at'],
                                                self.date_format),
                                msg_id = json_file['id_str'],
                                author_id = json_file['user']['id_str'],
                                author = json_file['user']['screen_name'],
                                color = 'green',
                                location = json_file['coordinates']
                )
                self.msg_queue.put(msg)
        else:
            return 0
