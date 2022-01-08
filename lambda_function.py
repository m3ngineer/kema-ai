import json
import logging
import sys
import psycopg2
import urllib
from datetime import datetime

from db import connect_to_rds, insert_into_table, select_from_table
from reminder import reminder_node_1
import conf

def check_user_thread_position(user_phone, data):
    ''' Checks for user's position in a flow '''

    sql = ''' SELECT
            trigger_message_sid, user_phone, thread_id, position_id, thread_data, update_datetime
        FROM kema_thread
        WHERE user_phone = %s
        ORDER BY update_datetime DESC LIMIT 1'''
    r = select_from_table(sql, (user_phone,))
    if r:
        return r[0][0], r[0][2], r[0][3]

    return None, None, None

def update_thread_position(data):
    ''' Updates a user's position in a flow '''
    pass

def lambda_inbound_message_handler(event, context):

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.info(event)

    # Format data stream to dictionary
    data = urllib.parse.unquote(event['body'])
    data = json.loads(data)
    # data = event['body']
    logger.info(data)

    user_phone = data['user_phone']
    # Check for position in previous conversation
    trigger_message_sid, thread_id, position_id = check_user_thread_position(user_phone, data)
    data['trigger_message_sid'] = trigger_message_sid
    # If last conversation not ended
    if thread_id:
        # continue conversation
        # Execute thread endpoint
        if thread_id == '1' and position_id == '1':
            reminder_node_1(data)
            # Replace with API endpoint eventually

    # Else start new conversation
    else:
        create_reminder()


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
        insert_into_table(data, 'kema_schedule')
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

event = {
"body": {
    "user_phone": conf.twilio_num_to,
    "from_": conf.twilio_num_from_,
    "thread_id": "1",
    "position_id": "1",
    "response": "2"
    }
}

# lambda_inbound_message_handler(event, None)
