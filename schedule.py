import re
import boto3
import itertools
import logging

from datetime import datetime, timedelta
from calendar import monthrange

class ScheduleParser():
    '''
    Takes in human-readable text time and extracts datetime to schedule a job
    '''
    def __init__(self, schedule_deadline_input, schedule_period_input):
        self.schedule_start, self.schedule_end = self.parse_date(schedule_deadline_input)
        self.schedule_weekdays = self.parse_period(schedule_period_input)

    def parse_date(self, text):
        '''
        Parses date from human-readable text
        '''

        def search_dict(input_list, input_dict):
            ''' Searches a list of texts for values in a dictionary and
            returns key of first matching value
            :param:input_list: list of text
            :param:input_dict: dictionary with keys as integers and values as list of text
            '''

            intersection = set(itertools.chain(*input_dict.values())).intersection(set(input_list))
            if len(intersection) > 0:
                value = list(intersection)[0]
                return next((k for k, v in input_dict.items() if value in v), None)
            return None

        def search_list(list1, list2):
            ''' Returns first matching value in 2 lists '''

            intersection = set(list1).intersection(set(list2))
            if len(intersection) > 0:
                return list(intersection)[0]
            return None

        days = {
            0: ['monday', 'mon'],
            1: ['tuesday', 'tues'],
            2: ['wednesday', 'wed', 'wednes'],
            3: ['thursday', 'thurs'],
            4: ['friday', 'fri'],
            5: ['saturday', 'sat'],
            6: ['sunday', 'sun'],
        }

        months = {
            1: ['jan','january'],
            2: ['feb','february'],
            3: ['mar','march'],
            4: ['apr','april'],
            5: ['may'],
            6: ['jun','june'],
            7: ['jul','july'],
            8: ['aug','august'],
            9: ['sep','sept','september'],
            10: ['oct','october'],
            11: ['nov','november'],
            12: ['dec','december']
        }

        text = [word.lower() for word in text.split()]
        current_date = datetime.now().date()

        schedule_start, schedule_end = current_date, current_date

        month = search_dict(text, months)
        if month:
            month_num_day = monthrange(current_date.year, month)[-1]
            day = search_list(
                    text,
                    list(str(i) for i in range(1,month_num_day+1))
                    )
            if day:
                schedule_end = datetime(
                                    current_date.year,
                                    month,
                                    int(day)
                                    ).date()
        return schedule_start.strftime('%Y-%m-%d'), schedule_end.strftime('%Y-%m-%d')

    def parse_period(self, text):
        '''
        Parses periodicity (days of a week) from human-readable text
        '''

        days = {
            0: ['monday', 'mon', 'mo', 'm'],
            1: ['tuesday', 'tues', 'tu'],
            2: ['wednesday', 'wed', 'wednes', 'we', 'w'],
            3: ['thursday', 'thurs', 'th'],
            4: ['friday', 'fri', 'fr'],
            5: ['saturday', 'sat', 'sa'],
            6: ['sunday', 'sun', 'su'],
        }

        weekdays = []

        if 'daily' or 'everyday' in text.lower():
            weekdays = list(range(7))
        elif 'weekend' in text.lower():
            weekdays = [5,6]
        elif 'weekday' or 'week day' in text.lower():
            weekdays = list(range(5))
        else:
            text = [word.lower() for word in text.split()]
            for word in text:
                for day_int, day_text in days.items():
                    if word == day_text:
                        weekdays.append(day_int)

        return ','.join([str(wkdy) for wkdy in weekdays])

    def schedule_job(self, dt):
        '''
        Schedules a job given a datetime object
        '''

        # Convert dt to chron time
        date = dt.date()
        month = date.month
        time = dt.time()
        day = dt.day
        weekday = dt.weekday()
        hour = dt.hour - 1
        min = dt.minute
        cron_expr = '{}, {}, {}, {}, {}, {}'.format('*', hour, day, month, '*', '*')

        # Put an event rule
        response = cloudwatch_events.put_rule(
            Name='DEMO_EVENT',
            RoleArn='IAM_ROLE_ARN',
            ScheduleExpression='cron({})'.format(cron_expr),
            State='ENABLED'
        )
        print(response['RuleArn'])

        # Put target for rule
        response = cloudwatch_events.put_targets(
            Rule='DEMO_EVENT',
            Targets=[
                {
                    'Arn': 'LAMBDA_FUNCTION_ARN',
                    'Id': 'myCloudWatchEventsTarget',
                }
            ]
        )
        print(response)

        # HOW END RESPONSE?

        pass
