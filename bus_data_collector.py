#!/usr/bin/python

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from datetime import timedelta
from Tables import Trip, Estimate, Base
import time
import requests
import random
import sys, getopt

baseUri = "https://api.octranspo1.com/v1.2/"
start_time_format = "%H:%M" # e.g. 20:48
request_time_format = "%Y%m%d%H%M%S" # e.g. 20161002130128

def getNextTripsForStop(appId, apiKey, stopNo = 6653, routeNo=85):
    r = requests.post(baseUri + "GetNextTripsForStop", data = {'appID':appId, 'apiKey' : apiKey, 'stopNo': stopNo, 'routeNo': routeNo, 'format': 'json'})
    return r.json()

def saveRequest(data, session):
    # Look up trip by start time
    route_data = data['GetNextTripsForStopResult']['Route']['RouteDirection']
    trips = route_data['Trips']['Trip']
    request_time = datetime.strptime(route_data['RequestProcessingTime'], request_time_format)
    for t in trips:
        start_time = datetime.strptime(t['TripStartTime'], start_time_format).time()
        trip = session.query(Trip).filter(Trip.start_time == start_time).first()
        # Create if doesn't exist
        if(trip is None):
            trip = Trip(route=route_data['RouteNo'],
                        start_time=start_time,
                        route_label=route_data['RouteLabel'])
        lat = None
        if t['Latitude'] != "":
            lat = float(t['Latitude'])
        lon = None
        if t['Longitude'] != "":
            lon = float(t['Longitude'])


        trip.estimates.append(Estimate(
            stop_id=data['GetNextTripsForStopResult']['StopNo'],
            estimate_processing_time=request_time,
            adjusted_schedule_time=t['AdjustedScheduleTime'],
            adjustment_age = float(t['AdjustmentAge']),
            latitude = lat,
            longitude = lon)
        )
        session.add(trip)
        session.commit()



def main(argv):
    minutes_to_run = 60
    route_number = 85
    stop_number = 6653

    help = 'bus_data_collector.py -r <route number> -s <stop number> -t <minutes to run> -a <api id> -k <api key>'

    try:
        opts, args = getopt.getopt(argv, "r:s:t:a:k:")
    except getopt.GetoptError:
        print(help)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(help)
            sys.exit()
        elif opt in ("-r"):
            route_number = arg
        elif opt in ("-s"):
            stop_number = arg
        elif opt in ("-t"):
            minutes_to_run = int(arg)
        elif opt in ("-a"):
            appId = arg
        elif opt in ("-k"):
            apiKey = arg



    engine = create_engine('sqlite:///ocbusdata.db')
    Base.metadata.bind = engine

    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=minutes_to_run)
    print("Starting at %s ending at %s" % (start_time, end_time))
    done = False

    while not done:
        iteration_time = datetime.now()
        next_trips = getNextTripsForStop(appId, apiKey, stop_number, route_number)
        saveRequest(next_trips, session)

        # Check when next estimate is
        trips = next_trips['GetNextTripsForStopResult']['Route']['RouteDirection']['Trips']['Trip']
        next_estimated_time = None
        for t in trips:
            trip_estimated_minutes = int(t['AdjustedScheduleTime'])
            if next_estimated_time is None or trip_estimated_minutes < next_estimated_time:
                next_estimated_time = trip_estimated_minutes

        # Gather more estimates when trips are close to arriving.
        if next_estimated_time > 10:
            next_request_wait = 300 # 5 minutes
        elif next_estimated_time > 5:
            next_request_wait = 180 # 3 minutes
        else:
            next_request_wait = 60 # 1 minute


        # Add a random factor
        next_request_wait += random.randint(0, 30)
        estimates = session.query(Estimate).count()
        trips = session.query(Trip).count()
        print("Next trip in %s minutes; checking again in %s seconds" % (next_estimated_time, next_request_wait))
        print("Now have %s estimates for %s trips" % (estimates, trips))

        if iteration_time >= end_time:
            done = True
        else:
            time.sleep(next_request_wait)


    print("Done.")

if __name__ == "__main__":
   main(sys.argv[1:])