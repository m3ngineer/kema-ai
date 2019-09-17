twilio_account_sid="AC2da36455d9bc7e8852949a1c254e5d79"
twilio_auth_token="788aa7f341567f67ebcbd2b884a4ffe2"

textit_voice='https://textit.in/mr/ivr/c/66939e54-47f8-405e-9d91-5293074faae4/incoming'
textit_message='https://textit.in/c/t/66939e54-47f8-405e-9d91-5293074faae4/receive'

RDS_host = 'sicling.cb4ysfubwurt.us-east-1.rds.amazonaws.com'
RDS_password = 'password'
RDS_user = 'meng_master'
RDS_port = 5432
RDS_db_name = 'sicling'

# curl -XPOST https://api.twilio.com/2010-04-01/Accounts/AC2da36455d9bc7e8852949a1c254e5d79/IncomingPhoneNumbers/PN9154329eaf302cd15185a6f7820a1ffd.json \
# --data-urlencode "SmsUrl=https://studio.twilio.com/v1/Flows/FWc0af0c20acf7eabf483e17bea0962bba/Executions" \
# -u 'AC2da36455d9bc7e8852949a1c254e5d79:788aa7f341567f67ebcbd2b884a4ffe2'
#
# curl -X POST "https://studio.twilio.com/v1/Flows/FWc0af0c20acf7eabf483e17bea0962bba/Executions"
# -d "To=+19148198579" -d "From=+19143369499" -u AC2da36455d9bc7e8852949a1c254e5d79:788aa7f341567f67ebcbd2b884a4ffe2
