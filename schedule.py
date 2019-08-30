import pandas as pd
from datetime import datetime, timedelta

def parse_date(text):
    '''
    Parses date from human-readable text
    '''

    def next_weekday(d, weekday):
        '''
            Get the next weekday as a date given a date d
            weekday: 0=Monday, 1=Tuesday...
        '''

        days_ahead = weekday - d.weekday()
        if days_ahead <= 0: # Target day already happened this week
            days_ahead += 7
        return d + timedelta(days_ahead)

    days = {
        0: ['monday', 'mon'],
        1: ['tuesday', 'tues'],
        2: ['wednesday', 'wed', 'wednes'],
        3: ['thursday', 'thurs'],
        4: ['friday', 'fri'],
        5: ['saturday', 'sat'],
        6: ['sunday', 'sun'],
    }

    text = [word.lower() for word in text.split()]
    current_date = datetime.now().date()

    if 'next' in text:
        # get the next weekday date
        for word in text:
            for weekday_num, weekday_words in days.items():
                if word in weekday_words:
                    weekday=weekday_num

        scheduled_date = next_weekday(current_date, weekday)

    elif 'today' in text:
        # assign to current date
        scheduled_date = current_date

    elif days.any() in text:
        # assign next available date equal to day
        weekday_phrases = [inner for outer in days.values() for inner in outer]

        pass

    # return date
    return scheduled_date

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

if __name__ == "__main__":

    tests = ['toay at 4 pm', '4pm today', 'tomorrow', 'today', 'whenever', 'in 4 hours'
    'end of day', 'eod', 'end of tomorrow', 'tomorrow afternoon']
    print(parse_date('today at 4 pm'))
    print(parse_date('next thurs at 4 pm'))
