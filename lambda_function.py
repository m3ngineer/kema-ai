import json
import logging
import sys
import psycopg2
import urllib
from datetime import datetime

from db import connect_to_rds, insert_into_table
import conf

def lambda_handler(event, context):
    ''' Inserts data from Twilio into RDS postgres database '''

    # Set logging
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.info(event)

    # Format data stream to dictionary
    data = urllib.parse.unquote(event['body'])
    data = json.loads(data)
    logger.info(data)

    # Connect to RDS instance
    try:
        conn = connect_to_rds()
    except:
        logger.error("ERROR: Unexpected error: Could not connect to psql RDS instance.")
        sys.exit()

    logger.info("SUCCESS: Connection to psql RDS instance succeeded")

    # Insert data into psql table
    try:
        insert_into_table(data, conn)
    except:
        logger.error("ERROR: Unexpected error: Could not insert data into psql RDS instance.")
        logger.debug(data)
        sys.exit()
    logger.info("SUCCESS: Inserted data into psql RDS instance")

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!'),
        'data': event
    }

def lambda_handler_send_reminder(event, context):

    to = conf.twilio_num_to
    from_ = conf.twilio_num_from_
    send_reminder(to, from_)

def send_reminder(to, from_):
    ''' Executes Reminder flow in Twilio to send a reminder checkin text '''

    client = Client(conf.twilio_account_sid, conf.twilio_auth_token)

    execution = client.studio \
                      .flows(conf.twilio_flow_sid) \
                      .executions \
                      .create(to=to, from_=from_)

    print(execution.sid)
