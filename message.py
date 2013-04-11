"""
Message class to represent standard message format
"""
import json

class Message(object):
    """
    Standard message format
    """
    def __init__(self, source, content, timestamp, msg_id=None,
                author_id=None, author=None, color='white', location=None):
        """
        Create a dictionary of msg format from its inputs
        """
        self.source = source 
        self.content = content 
        self.timestamp = timestamp
        self.msg_id = msg_id
        self.author_id = author_id
        self.author = author
        self.color = color
        self.location = location

    def to_json(self):
        """
        Transforms standard message into json string format
        """
        return json.dumps(self.__dict__)

class ShutdownSignal(object):
    """
    Shutdown message type to notify consumer threads to exit
    """
    def __init__(self):
        pass
