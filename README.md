# wheres-my-bus
This project is to analyze some data I've been gathering about how reliable (or, not so reliable...) the bus I take home from work is.

The data collection is done with bus\_data\_collector.py. To run this script, you will need to sign up and get an API id 
& key from http://www.octranspo.com/developers. This script calls the API to get estimated arrival times at slightly random intervals, 
getting more estimates when a bus is closer.

I also downloaded the GTFS schedule data from the same site, and used [pygtfs](http://pygtfs.readthedocs.io/en/latest/index.html) 
to create a database of the schedule data.