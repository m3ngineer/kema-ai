from twilio.rest import Client

import conf

def send_reminder(to, from_, data={}):
    ''' Executes Reminder flow in Twilio to send a reminder checkin text '''

    client = Client(conf.twilio_account_sid, conf.twilio_auth_token)

    execution = client.studio \
                      .flows(conf.twilio_flow_reminder_sid) \
                      .executions \
                      .create(to=to, from_=from_, parameters=data) \

    print('Sent message {}'.format(execution.sid))

if __name__ == "__main__":
    to = conf.twilio_num_to
    from_ = conf.twilio_num_from_
    send_reminder(to, from_)
