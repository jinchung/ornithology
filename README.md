
#Ornithology

Exploring threading module in Python for a sample producer-consumer problem
with filtering the Twitter realtime feeds API for specified keywords. 

##Usage
usage: supervisor.py [-h] [-u USERNAME] [-p PASSWORD]
                     [-k KEYWORDS [KEYWORDS ...]]

optional arguments:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        Please enter username for social accounts
  -p PASSWORD, --password PASSWORD
                        Please enter password for social accounts
  -k KEYWORDS [KEYWORDS ...], --keywords KEYWORDS [KEYWORDS ...]
                        Optional list of keywords withwhich to search social
                        media

##Wish List (in order)
* Make consumer writes data to datadump/database
* Separate synthetic processor that reads from file (no external APIs)
* Segregate the inside of the while True loops into easier-to-test functions
* Limit Queue size at instantiation
* Frontend visualization
* Test suite / unit testing
* Add one or two more APIs
* Indexing on incoming data
