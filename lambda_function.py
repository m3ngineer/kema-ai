import json
import logging
import sys
from sqlalchemy import create_engine
import pymysql
import psycopg2
import urllib

import conf

def connect_to_rds(return_engine=False):
    ''' Connects to RDS and returns connection '''
    conn = psycopg2.connect(database=conf.RDS_db_name,
                    host=conf.RDS_host,
                    user=conf.RDS_user,
                    password=conf.RDS_password)
    return conn

# try:
#     connect_to_rds()

# except:
#     logger.error("ERROR: Unexpected error: Could not connect to MySql instance.")
#     sys.exit()

# logger.info("SUCCESS: Connection to RDS mysql instance succeeded")

def lambda_handler(event, context):

    # logging
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.info(event)

    data = urllib.parse.unquote(event['body'])
    logger.info(data)

    def insert_into_table(data, conn):
        '''
        Insert data from execution flow into table
        data: dict {user_id: str, task: str, barrier: str, possibility: str, schedule:
            str, date: datetime}
        '''

        conn = connect_to_rds()

        # Assign variables
        print(data)
        trigger_message_sid = data['trigger_message_sid']
        user_phone = data['username']
        trigger_text = data['trigger_text']
        task = data['task']#.replace('\n', '')
        barrier = data['barrier']
        possibility = data['possibility']
        scheduled_time_text_input = data['scheduled_time_text_input']
        scheduled_time = data['scheduled_time']
        update_datetime = datetime.now().isoformat()

        # Insert into table
        insert_sql = """INSERT INTO kema_ai
                    (trigger_message_sid, user_phone, trigger_text
                    task, barrier, possibility, scheduled_time_text_input,
                    scheduled_time, update_datetime)
                    VALUES ({}, {}, {}, {}, {}, {}, {}, {}, {})
                    """.format(trigger_message_sid, user_phone, trigger_text,
                        task, barrier, possibility, scheduled_time_text_input,
                        scheduled_time, update_datetime)

        conn.execute(text(insert_sql))

    conn = connect_to_rds()

    insert_into_table(data, conn)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!'),
        'data': event
    }
