
"""
Main entry point for the app
"""

from twisted.internet import reactor
from twisted.internet import task

from autobahn.websocket import listenWS

import argparse
import ConfigParser
import signal

import server
import monitor

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

def clean_exit(*unused):
    """
    Clean exit when user presses Ctrl + C
    Closes threads, websockets, and shared
    data structures
    """
    del unused
    SERVER_FACTORY.clean_exit()
    reactor.stop()

if __name__ == "__main__":
    ARGS = parse_args()
    CONFIG = get_config()

    MONITOR_HOST = CONFIG['MonitorSocket']['host']
    MONITOR_PORT = CONFIG['MonitorSocket']['port']
    MONITOR_URL = 'ws://' + MONITOR_HOST + ':' + MONITOR_PORT

    MONITOR_FACTORY = monitor.MonitorServerFactory(MONITOR_URL)
    MONITOR_FACTORY.protocol = monitor.MonitorServerProtocol
    listenWS(MONITOR_FACTORY)

    SERVER_HOST = CONFIG['ServerSocket']['host']
    SERVER_PORT = CONFIG['ServerSocket']['port']
    SERVER_URL = 'ws://' + SERVER_HOST + ':' + SERVER_PORT

    SERVER_FACTORY = server.ServerFactory(SERVER_URL, MONITOR_FACTORY,
                                          CONFIG, ARGS.dev)
    print "in main: server_factory created... "
    signal.signal(signal.SIGINT, clean_exit)
    SERVER_FACTORY.protocol = server.ServerProtocol
    SERVER_FACTORY.setup()
    listenWS(SERVER_FACTORY)

    MONITOR_TASK = task.LoopingCall(SERVER_FACTORY.monitor_callback)
    MONITOR_TASK.start(1)
    reactor.run()

