from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse
from datetime import datetime
import requests

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
        body = request.form.get('body') # data as bytes str
        task = request.form.get('task')
        barrier = request.form.get('barrier')
        possibility = request.form.get('possibility')
        schedule = request.form.get('schedule')

        data = {'task': str(task),
                'barrier': str(barrier),
                'possibility': str(possibility),
                'schedule': str(schedule),
                'date': datetime.now().strftime('%Y-%m-%d:%H:%m')}

        print(data)
        
        # Make another post request
        # response = requests.post(
        #     url, data=json.dumps(data),
        #     headers={'Content-Type': 'application/json'}
        # )

    return str(data)

if __name__ == "__main__":
    app.run(debug=True)
