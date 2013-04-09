"""
NYT User: Jin's email
NYT Pwd: ornithology
Application Registration Name: Ornithology
Times Newswire API Key: 7831b763eca627bc9b2967a43cb8a5e6:3:67531365
"""

import json
import pycurl
import time

import producer

class NYTProducer(producer.Producer):
    """
    Base producer class for NYT API
    """

    def __init__(self, msg_queue):
        super(NYTProducer, self).__init__(msg_queue)

        self.date_format = '%Y-%m-%dT%H:%M:%S'

        self.apikey = '7831b763eca627bc9b2967a43cb8a5e6:3:67531365'

        self.buffer = ""
        self.stream_url = ("http://api.nytimes.com/svc/news/v3/content/all"
                          "/all.json?api-key=" + self.apikey)
        self.conn = pycurl.Curl()
        self.conn.setopt(pycurl.URL, self.stream_url)
        self.conn.setopt(pycurl.WRITEFUNCTION, self.write_function)

    def run(self):
        while True:
            self.conn.perform()
            if self.buffer:
                json_content = json.loads(self.buffer)
                self.parse(json_content)

            self.buffer = ""
            time.sleep(20) # max allowed requests for NYT Newswire API
                           # is 5000 requests per day

    def parse(self, json_content):
        """
        Parse the content of the API's json response
        into our predefined msg format
        """
        for json_file in json_content["results"]:
            msg = self.msg_dict(
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

