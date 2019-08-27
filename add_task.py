import requests
from requests.auth import HTTPBasicAuth
from twilio.rest import Client

import conf

def execute_task():
    params = {
    'To': '+19148198579',
    'From': '+19143369499'
    }

    client = Client(conf.twilio_account_sid, conf.twilio_auth_token)

    execution = client.studio \
                      .flows('FWc0af0c20acf7eabf483e17bea0962bba') \
                      .executions \
                      .create(to='+19148198579', from_='+19143369499')

    print(execution.sid)

if __name__ == "__main__":
    print(execute_task())
