"""
NYT Producer, passes NYC articles/blogs to consumer(s)
"""

import json
import pycurl
import time

import producer
import message

class NYTProducer(producer.Producer):
    """
    Base producer class for NYT API
    """

    def __init__(self, api_key, msg_queue):
        super(NYTProducer, self).__init__(msg_queue)

        self.date_format = '%Y-%m-%dT%H:%M:%S'
        self.apikey = api_key
        self.buffer = ""
        self.stream_url = ("http://api.nytimes.com/svc/news/v3/content/all"
                          "/all.json?api-key=" + self.apikey)
        self.conn = pycurl.Curl()
        self.conn.setopt(pycurl.URL, self.stream_url)
        self.conn.setopt(pycurl.WRITEFUNCTION, self.write_function)
        self.conn.setopt(pycurl.NOSIGNAL, 1)

    def run(self):
        while self.alive:
            self.conn.perform()
            if self.buffer:
                try:
                    json_content = json.loads(self.buffer)
                    self.parse(json_content)
                except ValueError:
                    pass
            self.buffer = ""
            time.sleep(20) # max allowed requests for NYT Newswire API
                           # is 5000 requests per day
        self.conn.close()

    def parse(self, json_content):
        """
        Parse the content of the API's json response
        into our predefined msg format
        """
        for json_file in json_content["results"]:
            msg = message.MediaMessage(
                    source = 'NYT',
                    content = json_file['title'] +
                                ' - ' + json_file['abstract'],
                    timestamp = self.parse_time(
                                    json_file['updated_date'],
                                    self.date_format),
                    msg_id = hash(json_file['byline'] +
                                 json_file['created_date']),
                    author = json_file['byline'],
                    color = 'white',
                    location = json_file['geo_facet']
            )
            self.msg_queue.put(msg)

    def write_function(self, data):
        """
        Callback for pycurl to write to buffer
        """
        self.buffer += data

