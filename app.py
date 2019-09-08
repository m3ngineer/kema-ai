from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse
from datetime import datetime
import requests

from schedule import parse_datetime

import db

app = Flask(__name__)

@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():

    # Print response
    message_body = request.form['Body']
    print(message_body)

    # Start a response
    resp = MessagingResponse()

    # Add a message
    resp.message(' Got it, thanks for responding!')
    return str(resp)

@app.route("/response", methods=['GET', 'POST'])
def store_data():

    if request.method == 'POST':
        user_phone = request.form.get('user_phone')
        trigger_text = request.form.get('trigger_text')
        trigger_instance_sid = request.form.get('trigger_instance_sid')
        body = request.form.get('body') # data as bytes str
        task = request.form.get('task')
        barrier = request.form.get('barrier')
        possibility = request.form.get('possibility')
        scheduled_time_text_input = request.form.get('schedule')
        scheduled_time = parse_datetime(scheduled_time_text_input)

        data = {
                'trigger_message_sid': trigger_message_sid,
                'user_phone': str(user_phone),
                'trigger_text': str(trigger_text),
                'task': str(task),
                'barrier': str(barrier),
                'possibility': str(possibility),
                'scheduled_time_text_input': str(scheduled_time_text_input),
                'scheduled_time': scheduled_time,
                'update_datetime': datetime.now().strftime('%Y-%m-%d:%H:%m'),
                }

        print(data)

        insert_into_table(data)

        # Make another post request
        # response = requests.post(
        #     url, data=json.dumps(data),
        #     headers={'Content-Type': 'application/json'}
        # )

    return str(data)

if __name__ == "__main__":
    app.run(debug=True)
