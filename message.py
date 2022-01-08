from twilio.rest import Client
import os

import conf

def send_msg(msg, to, from_):

    account_sid = conf.twilio_account_sid
    auth_token = conf.twilio_auth_token
    client = Client(account_sid, auth_token)

    twi_msg = client.messages \
                    .create(
                         body=msg,
                         from_=from_,
                         to=to
                     )
