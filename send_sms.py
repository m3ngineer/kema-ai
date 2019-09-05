# Download the helper library from https://www.twilio.com/docs/python/install
from twilio.rest import Client
import os

# Your Account Sid and Auth Token from twilio.com/console
# DANGER! This is insecure. See http://twil.io/secure
account_sid = conf.twilio_account_sid
auth_token = conf.twilio_auth_token
client = Client(account_sid, auth_token)

def add_task():
    message = client.messages \
                    .create(
                         body="What have you not done this week that you would like to accomplish?",
                         from_='+19143369499',
                         to='+19148198579'
                     )

    print(message.sid)
