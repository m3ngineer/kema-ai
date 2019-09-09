import requests
from requests.auth import HTTPBasicAuth
from twilio.rest import Client

import conf

def lambda_handler(event, context):

    to = '+19148198579'
    from_ = '+19143369499'
    send_reminder(to, from_)

def send_reminder(to, from_):
    ''' Executes Reminder flow in Twilio to send a reminder checkin text '''

    # params = {
    # 'To': to,
    # 'From': from_
    # }

    client = Client(conf.twilio_account_sid, conf.twilio_auth_token)

    execution = client.studio \
                      .flows('FWc0af0c20acf7eabf483e17bea0962bba') \
                      .executions \
                      .create(to=to, from_=from_)

    print(execution.sid)

if __name__ == "__main__":
    to = '+19148198579'
    from_ = '+19143369499'
    send_reminder(to, from_)
