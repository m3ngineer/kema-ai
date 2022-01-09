import psycopg2
import logging
import json
from datetime import datetime

from schedule import ScheduleParser
import conf

def connect_to_rds():
    ''' Connects to RDS and returns connection '''

    conn = psycopg2.connect(database=conf.RDS_db_name,
                    host=conf.RDS_host,
                    user=conf.RDS_user,
                    password=conf.RDS_password)
    return conn

def create_tables(table, drop_table=False):
    ''' Creates tables in RDS database '''
    conn = connect_to_rds()
    cursor = conn.cursor()

    if drop_table:
        try:
            sql = 'DROP TABLE {};'.format(table)
            cursor.execute(sql)
            print('table {} dropped'.format(table))
        except:
            pass

    # Create new tables
    if table == 'kema_schedule':
        create_table_sql  = """
                CREATE TABLE kema_schedule (
                trigger_message_sid VARCHAR PRIMARY KEY,
                user_phone VARCHAR,
                trigger_text VARCHAR,
                task VARCHAR,
                barrier VARCHAR,
                possibility VARCHAR,
                schedule_deadline_input VARCHAR,
                schedule_period_input VARCHAR,
                schedule_start DATE,
                schedule_end DATE,
                schedule_weekdays VARCHAR,
                schedule_time TIMESTAMP,
                update_datetime TIMESTAMP
                );
                """
    elif table == 'kema_thread':
        create_table_sql  = """
                CREATE TABLE kema_thread (
                trigger_message_sid VARCHAR PRIMARY KEY,
                user_phone VARCHAR,
                thread_id VARCHAR,
                position_id VARCHAR,
                thread_data VARCHAR,
                update_datetime TIMESTAMP
                );
                """
    else:
        raise ValueError('Table {} not found.'.format(table))

    cursor.execute(create_table_sql)
    print('{} table created.'.format(table))
    conn.commit()
    conn.close()

def insert_into_table(data, table):
    '''
    Insert data from execution flow into table
    data: dict {user_id: str, task: str, barrier: str, possibility: str, schedule:
        str, date: datetime}
    '''

    conn = connect_to_rds()
    cursor = conn.cursor()
    logger = logging.getLogger()

    if table == 'kema_schedule':
        schedule_parser = ScheduleParser(
                            data['schedule_deadline_input'],
                            data['schedule_period_input']
                            )

        # Assign variables
        trigger_message_sid = data['trigger_message_sid']
        user_phone = data['user_phone']
        trigger_text = data['trigger_text']
        task = data['task']
        barrier = data['barrier']
        possibility = data['possibility']
        schedule_deadline_input = data['schedule_deadline_input']
        schedule_period_input = data['schedule_period_input']
        schedule_start = schedule_parser.schedule_start
        schedule_end = schedule_parser.schedule_end
        schedule_weekdays = schedule_parser.schedule_weekdays
        schedule_time = datetime.now()
        update_datetime = datetime.now()

        # Insert into table
        insert_sql = """INSERT INTO kema_schedule
                    (trigger_message_sid, user_phone, trigger_text,
                    task, barrier, possibility, schedule_deadline_input,
                    schedule_period_input, schedule_start, schedule_end,
                    schedule_weekdays, schedule_time, update_datetime)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """

        try:
            cursor.execute(insert_sql, (trigger_message_sid, user_phone, trigger_text,
                task, barrier, possibility, schedule_deadline_input,
                schedule_period_input, schedule_start, schedule_end,
                schedule_weekdays, schedule_time, update_datetime,))
            conn.commit()
            logger.info('Execution {} inserted into kema_schedule'.format(trigger_message_sid))

        except Exception as e:
            raise

    elif table == 'kema_thread':
        try:
            # Assign variables
            trigger_message_sid = data['trigger_message_sid']
            user_phone = data['user_phone']
            thread_id = data['thread_id']
            position_id = data['position_id']
            update_datetime = datetime.now()

            # Insert into table
            insert_sql = """INSERT INTO kema_thread
                        (trigger_message_sid, user_phone, thread_id, position_id,
                        update_datetime)
                        VALUES (%s, %s, %s, %s, %s)
                        """
            cursor.execute(insert_sql, (trigger_message_sid, user_phone, thread_id, position_id,
                update_datetime,))
            conn.commit()
            logger.info('Thread for user {} updated in kema_thread'.format(user_phone))

        except Exception as e:
            raise

    conn.close()

def select_from_table(query, params=()):
    '''
    Extract data from table
    :param:query: str
    '''

    conn = connect_to_rds()
    cursor = conn.cursor()

    try:
        cursor.execute(query, params)
        r = cursor.fetchall()
    except Exception as e:
        raise

    conn.close()
    return r

def update_table(query, params):
    '''
    :param: query: str
    :param: params: tuple
    '''

    conn = connect_to_rds()
    cursor = conn.cursor()

    try:
        cursor.execute(query, params)
        conn.commit()
    except Exception as e:
        raise

    conn.close()

if __name__ == '__main__':
    # create_tables('kema_schedule', drop_table='kema_schedule')
    create_tables('kema_thread', drop_table='kema_thread')
    data = {
        'trigger_message_sid': 'test',
        'user_phone': conf.twilio_num_to,
        'thread_id': '1',
        'position_id': '1',
    }

    insert_into_table(data, 'kema_thread')

    # data = {
    #     'trigger_message_sid': 'test',
    #     'user_phone':conf.twilio_num_to,
    #     'trigger_text':'test',
    #     'task':'test',
    #     'barrier':'test',
    #     'possibility':'test',
    #     'schedule_deadline_input':'mar 1',
    #     'schedule_period_input':'daily',
    #     '':'',
    #
    # }
    # insert_into_table(data, 'kema_schedule')
