import json
import logging
import sys
import psycopg2
import urllib
from datetime import datetime

import conf

def connect_to_rds(return_engine=False):
    ''' Connects to RDS and returns connection '''
    conn = psycopg2.connect(database=conf.RDS_db_name,
                    host=conf.RDS_host,
                    user=conf.RDS_user,
                    password=conf.RDS_password)
    return conn

def insert_into_table(data, conn):
    '''
    Insert data from execution flow into table
    data: dict {trigger_message_sid: str, user_phone: str, task: str,
        barrier: str, possibility: str, scheduled_time_text_input: str,
        scheduled_time: datetime, update_datetime: datetime}
    '''

    # Assign variables
    trigger_message_sid = data['trigger_message_sid']
    user_phone = data['user_phone']
    trigger_text = data['trigger_text']
    task = data['task'] #.replace('\n', '')
    barrier = data['barrier']
    possibility = data['possibility']
    scheduled_time_text_input = data['scheduled_time_text_input']
    scheduled_time = datetime.now().isoformat()
    update_datetime = datetime.now().isoformat()

    # Insert into table
    insert_sql = """INSERT INTO kema_ai
                (trigger_message_sid, user_phone, trigger_text,
                task, barrier, possibility, scheduled_time_text_input,
                scheduled_time, update_datetime)
                VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')
                """.format(trigger_message_sid, user_phone, trigger_text,
                    task, barrier, possibility, scheduled_time_text_input,
                    scheduled_time, update_datetime)
    print(insert_sql)

    cursor = conn.cursor()
    cursor.execute(insert_sql)
    conn.commit()
    cursor.close()

def lambda_handler(event, context):
    ''' Inserts data from Twilio into RDS postgres database '''

    # Set logging
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
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
        logger.info()
        sys.exit()
    logger.info("SUCCESS: Inserted data into psql RDS instance")

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!'),
        'data': event
    }
