from datetime import datetime, timedelta
import re
import boto3

class ScheduleJob():
    '''
    Takes in human-readable text time and extracts datetime to schedule a job
    '''
    def __init__(self, text):
        self.scheduled_datetime = self.parse_datetime(text)

    def parse_date(self, text):
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
        scheduled_date = current_date

        if 'today' in text:
            return scheduled_date
        elif 'tomorrow' in text:
            return current_date + timedelta(1)
        else:
            weekday_phrases = [inner for outer in days.values() for inner in outer]
            # get the next weekday date
            found = False
            for word in text:
                for weekday_phrase in weekday_phrases:
                    if word == weekday_phrase:
                        weekday = word
                        scheduled_date = next_weekday(current_date, weekday)
                        break
                if found:
                    break

        # return date
        return scheduled_date

    def parse_time(self, text):
        '''
        Parses time from human-readable text
        Does not deal with minutes yet
        '''

        scheduled_time = datetime.strptime('12:00', '%H:%M').time()

        current_time = datetime.now().time()

        try:
            ints_str = [str(i) for i in list(range(1, 25))]
            if re.findall('at ?\d+\s?a?p?m?.*', text.lower()):
                hour =  re.findall('at ?\d+\s?a?p?m?.*', text.lower())
                hour = hour[0].replace('at', '').replace('pm', '').replace('am', '').replace(' ', '')
            elif re.findall(' ?\d+ *a?p?m?.*', text.lower()):
                hour = re.findall(' ?\d+\s?a?p?m?.*', text.lower())
                hour = hour[0].replace('at', '').replace('pm', '').replace('am', '').replace(' ', '')
            else:
                return scheduled_time

            if 'pm' in text:
                scheduled_time = datetime.strptime('{} PM'.format(hour), '%I %p').time()
            elif 'am' in text:
                scheduled_time = datetime.strptime('{} AM'.format(hour), '%I %p').time()
            else:
                # If user doesn't specify am/pm, choose most logical
                if int(hour) in list(range(1,7)): # Likely PM
                    scheduled_time = datetime.strptime('{} PM'.format(hour), '%I %p').time()
                else:
                    scheduled_time = datetime.strptime('{} AM'.format(hour), '%I %p').time()
        except Exception as e:
            print(e)

        return scheduled_time

    def parse_datetime(self, text):
        '''
        Converts date and time to datetime object
        '''

        # Parse date and time
        scheduled_date = self.parse_date(text)
        scheduled_time = self.parse_time(text)

        # Combine date and time
        datetime_as_str = '{}-{}-{} {}:00'.format(
                                            scheduled_date.year,
                                            scheduled_date.month,
                                            scheduled_date.day,
                                            scheduled_time.hour,
                                            )
        scheduled_datetime = datetime.strptime(datetime_as_str, '%Y-%m-%d %H:00')

        return scheduled_datetime

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
