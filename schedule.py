import pandas as pd
from datetime import datetime, now, timedelta

def parse_date(text):
    '''
    Parses date from human-readable text
    '''

    days = {
    'mon': ['monday', 'mon'],
    'tues': ['tuesday', 'tues'],
    'wed': ['wednesday', 'wed', 'wednes'],
    'thurs': ['thursday', 'thurs'],
    'fri': ['friday', 'fri'],
    'sat': ['saturday', 'sat'],
    'sun': ['sunday', 'sun'],
    }

    text = [word.lower() for word in text.split()]
    if 'next' in text:
        # create min date
        # assign to next week
        pass
    elif 'today' in text:
        # assign to current date
        pass
    elif days.any() in text:
        # assign next available date equal to day
        pass

    # return date
    pass

def parse_time(text):
    '''
    Parses time from human-readable text
    '''
    pass

def convert_to_datetime():
    '''
    Converts date and time to datetime object
    '''
    pass

def schedule_job(dt):
    '''
    Schedules a job given a datetime object
    '''
    pass
