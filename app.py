from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse

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

if __name__ == "__main__":
    app.run(debug=True)
