#Ornithology

Exploring threading module in Python for a sample producer-consumer problem
with filtering API feeds for specified keywords. 

##Architecture
###supervisor
* Entry point of the application
* Spawns all producer threads and the consumer thread
* Manages benchmark metrics

###producer
* Abstract class implemented by subclasses for each social media
* Manages connections to external APIs and pushes data to consumer via queue

###consumer
* Single consumer which reads data from producers and searches for keywords
specified by user (or default)
* Updates metrics after processing messages

##Usage
<pre>
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
</pre>

##Wish List (in order)
* Glyph code review
* Frontend visualization
* Test suite / unit testing
* Add one or two more APIs
* Indexing on incoming data

