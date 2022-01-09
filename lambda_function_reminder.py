import json
import logging
import sys
import psycopg2
import urllib
from datetime import datetime

from reminder import send_reminder
from db import connect_to_rds, select_from_table, update_table
import conf

def lambda_handler_send_reminder(event, context):
    ''' Executes reminder Flow in Twilio '''

    # Set logging
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.info(event)

    # Connect to RDS instance
    try:
        conn = connect_to_rds()
    except:
        logger.error("ERROR: Unexpected error: Could not connect to psql RDS instance.")
        sys.exit()

    logger.info("SUCCESS: Connection to psql RDS instance succeeded")

    # Extract data from postgres table
    try:
        sql = """
            SELECT DISTINCT
                trigger_message_sid, user_phone, task, possibility, barrier, schedule_start, schedule_end, schedule_weekdays
            FROM
                kema_schedule
            WHERE
                CURRENT_DATE BETWEEN schedule_start AND schedule_end;
        """
        reminders = select_from_table(sql)
    except:
        logger.error("ERROR: Unexpected error: Could not query data from RDS instance.")
        # logger.debug(data)
        sys.exit()

    # For every item in list
    from_ = conf.twilio_num_from_
    for (trigger_message_sid, to, task, possibility, barrier, schedule_start, schedule_end, schedule_weekdays) in reminders:
        data = {'trigger_message_sid': trigger_message_sid, 'task':task.lower(), 'barrier':barrier.lower()}
        send_reminder(to, from_, data=data)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!'),
        'data': event
    }

def lambda_handler_end_reminder(event, context):
    ''' Ends scheduled reminder '''

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

    try:
        current_date = datetime.now()
        trigger_message_sid = data['trigger_message_sid']

        sql = '''
            UPDATE kema_schedule
            SET schedule_end = %s,
                update_time = %s
            WHERE trigger_message_sid = %s
            '''

        params = (current_date, current_date, trigger_message_sid)
        update_table(sql, params)
    except:
        logger.error("ERROR: Unexpected error: Could not update data from RDS instance.")
        # logger.debug(data)
        sys.exit()

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!'),
        'data': event
    }

def lambda_handler_update_db(event, context):
    ''' Updates field in database '''

    # Set logging
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.info(event)

    # Format data stream to dictionary
    data = urllib.parse.unquote(event['body'])
    data = json.loads(data)

    try:
        current_date = datetime.now()
        origin_trigger_message_sid = data['origin_trigger_message_sid']
        new_barrier = data['barrier']

        # Select past barrier
        sql = """
            SELECT DISTINCT
                trigger_message_sid, barrier
            FROM
                kema_schedule
            WHERE trigger_message_id = %s;
        """
        prev_barriers = select_from_table(sql, (origin_trigger_message_sid))

        for (trigger_message_sid, prev_barrier) in list_barriers[0]:
            updt_barriers = ','.join([prev_barrier,new_barrier])

            sql = '''
                UPDATE kema_schedule
                SET barrier = %s,
                    update_time = %s
                WHERE trigger_message_sid = %s;
                '''

            params = (updt_barriers, current_date, origin_trigger_message_sid)
            update_table(sql, params)
    except:
        logger.error("ERROR: Unexpected error: Could not update data from RDS instance.")
        # logger.debug(data)
        sys.exit()

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!'),
        'data': event
    }
