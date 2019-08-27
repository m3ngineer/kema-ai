import requests
from requests.auth import HTTPBasicAuth

import conf

def add_task():
    params = {
    'To': '+19148198579',
    'From': '+19143369499'
    }

    r = requests.post('https://studio.twilio.com/v1/Flows/FWc0af0c20acf7eabf483e17bea0962bba/Executions',
        params=params,
        auth=(conf.twilio_account_sid, conf.twilio_auth_token))

    return r

if __name__ == "__main__":
    print(add_task())
