import json
import logging
import sys
import psycopg2
import urllib
from datetime import datetime

from db import connect_to_rds, insert_into_table, select_from_table, clear_thread_for_user_phone
from reminder import (reminder_node_1, reminder_node_2, reminder_node_3,
    reminder_node_4, reminder_node_5, reminder_node_6,
    create_reminder, create_node_1, create_node_2,
    create_node_3, create_node_4, create_node_5, delete_reminder,
    delete_reminder_node_1, retrieve_menu)
from message import send_msg
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

def lambda_inbound_message_handler(event, context):

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.info(event)

    # Format data stream to dictionary
    data = urllib.parse.unquote(event['body'])
    data = json.loads(data)
    # data = event['body']
    logger.info(data)

    ###### FOR TESTING ########
    # from twilio.rest import Client
    # from message import send_msg
    # send_msg('This is a test message', conf.twilio_num_to, conf.twilio_num_from_)
    ###### FOR TESTING ########

    user_phone = data['user_phone']
    # Check for position in previous conversation
    trigger_message_sid, thread_id, position_id = check_user_thread_position(user_phone, data)
    if trigger_message_sid:
        # Reset trigger message SID if continuing a conversation thread
        data['trigger_message_sid'] = trigger_message_sid
        # Clear any other threads
        clear_thread_for_user_phone(user_phone, exclude_trigger_message_sid=trigger_message_sid)

    # Check for STOP request and exist all threads if found
    if data['trigger_text'].lower() in ('stop', 'exit'):
        clear_thread_for_user_phone(user_phone)
        send_msg('Ok, restarting all conversations.', conf.twilio_num_to, conf.twilio_num_from_)
        return

    # Tigger thread to delete task
    if 'delete' in data['trigger_text'].lower() or 'delete task' in data['trigger_text'].lower():
        delete_reminder(data)
        return

    # Tigger thread to delete task
    if 'menu' in data['trigger_text'].lower() or 'option' in data['trigger_text'].lower():
        retrieve_menu(data)
        return

    # If last conversation not ended
    print(trigger_message_sid, thread_id, position_id)
    if thread_id == '1':
        # Continue thread to send reminder
        if position_id == '1':
            # Ask barrier
            reminder_node_1(data) # Replace with API endpoint eventually
        elif position_id == '2':
            # Update barrier for single task
            reminder_node_2(data)
        elif position_id == '3':
            # Check status or ask barrier for multi-task
            reminder_node_3(data)
        elif position_id == '4':
            # Update barrier for multiple task
            reminder_node_4(data)
        elif position_id == '5':
            # End or update schedule for completed tasks
            reminder_node_5(data)
        elif position_id == '6':
            # End or update schedule for completed tasks (multiple)
            reminder_node_6(data)
        else:
            raise ValueError('position_id {} does not exist for thread_id {}'.format(position_id, thread_id))

    elif thread_id == '0':
        # Continue thread to create new reminder
        if position_id == '1':
            create_node_1(data) # Replace with API endpoint eventually
        elif position_id == '2':
            create_node_2(data)
        elif position_id == '3':
            create_node_3(data)
        elif position_id == '4':
            create_node_4(data)
        elif position_id == '5':
            create_node_5(data)
        else:
            raise ValueError('position_id {} does not exist for thread_id {}'.format(position_id, thread_id))

    elif thread_id == '2':
        # Continue thread to create new reminder
        if position_id == '1':
            delete_reminder_node_1(data) # Replace with API endpoint eventually
        else:
            raise ValueError('position_id {} does not exist for thread_id {}'.format(position_id, thread_id))

    # Else start new task
    else:
        print('Clearing thread')
        clear_thread_for_user_phone(user_phone)
        create_reminder(data)


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
    "position_id": "3",
    "response": "2"
    }
}

# lambda_inbound_message_handler(event, None)
