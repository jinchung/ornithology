
#Ornithology

Exploring threading module in Python for a sample producer-consumer problem
with filtering the Twitter realtime feeds API for specified keywords. 

##Usage

For PROD mode:
`$ python supervisor.py uSeRnAme Pa$$w0rD`

or for DEV mode:
`$ python supervisor.py -D uSeRnAme Pa$$w0rD`

DEV mode does not create a new connection to the Twitter streaming API 
but instead uses pickled tweets for testing purposes.
