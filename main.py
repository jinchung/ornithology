
import argparse
import ConfigParser
import signal

import supervisor

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
    SUPER = Supervisor(CONFIG, ARGS.dev)
    signal.signal(signal.SIGINT, SUPER.clean_exit)
    SUPER.launch()

