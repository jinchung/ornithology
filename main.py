
from twisted.internet import reactor
from twisted.internet import task

from autobahn.websocket import listenWS

import argparse
import ConfigParser
import signal

import server

def parse_args():
    """
    Argument setup and parsing
    """
    parser = argparse.ArgumentParser()
   
    parser.add_argument('-d', '--dev',
                        help='Specify dev mode or not (default is PROD)',
                        action='store_true')

    return parser.parse_args()

def get_config():
    """
    Retrieve and parse system config file
    """
    config = ConfigParser.RawConfigParser()
    config.read('ornithology.cfg')
    return {section:dict(config.items(section)) 
            for section in config.sections()}

if __name__ == "__main__":
    ARGS = parse_args()
    CONFIG = get_config()

    host = CONFIG['WebSocket']['host']
    port = CONFIG['WebSocket']['port']

    server_url = 'ws://' + host + ':' + port
    factory = server.ServerFactory(server_url, CONFIG, ARGS.dev)
    signal.signal(signal.SIGINT, factory.clean_exit)
    factory.protocol = server.ServerProtocol
    factory.setup()
    listenWS(factory)

    monitor_task = task.LoopingCall(factory.monitor_callback)
    monitor_task.start(1)
    reactor.run()

