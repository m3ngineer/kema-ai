import psycopg2
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

def create_tables(drop_table=False):
    ''' Creates post_metric table in RDS database '''
    conn = connect_to_rds()
    cursor = conn.cursor()

    if drop_table:
        try:
            sql = 'DROP TABLE {};'.format(drop_table)
            cursor.execute(sql)
            print('table {} dropped'.format(table))
        except:
            pass

    # Create new tables
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
            schedule_start DATETIME,
            schedule_end DATETIME,
            schedule_weekdays VARCHAR,
            scheduled_time TIMESTAMP,
            update_datetime TIMESTAMP
            );
            """

    cursor.execute(create_table_sql)
    print('kema_schedule table created.')
    conn.close()

def insert_into_table(data):
    '''
    Insert data from execution flow into table
    data: dict {user_id: str, task: str, barrier: str, possibility: str, schedule:
        str, date: datetime}
    '''

    conn = connect_to_rds()
    cursor = conn.cursor()

    schedule_parser = ScheduleParser(
                        data['schedule_deadline_input'],
                        data['schedule_period_input']
                        )

    logger = logging.getLogger()
    logger.info(schedule_parser.schedule_start)
    logger.info(schedule_parser.schedule_end)
    logger.info(schedule_parser.schedule_weekdays)

    # Assign variables
    trigger_message_sid = data['trigger_message_sid']
    user_phone = data['user_phone']
    trigger_text = data['trigger_text']
    task = data['task']#.replace('\n', '')
    barrier = data['barrier']
    possibility = data['possibility']
    schedule_deadline_input = data['schedule_deadline_input']
    schedule_period_input = data['schedule_period_input']
    schedule_start = schedule_parser.schedule_start
    schedule_end = schedule_parser.schedule_end
    schedule_weekdays = schedule_parser.schedule_weekdays
    schedule_time = datetime.now().isoformat()
    update_datetime = datetime.now().isoformat()

    # Insert into table
    insert_sql = """INSERT INTO kema_schedule
                (trigger_message_sid, user_phone, trigger_text
                task, barrier, possibility, schedule_deadline_input,
                schedule_period_input, schedule_start, schedule_end,
                schedule_weekdays, schedule_time, update_datetime)
                VALUES ({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}
                """.format(trigger_message_sid, user_phone, trigger_text,
                    task, barrier, possibility, schedule_deadline_input,
                    schedule_period_input, schedule_start, schedule_end,
                    schedule_weekdays, schedule_time, update_datetime)

    try:
        cursor.execute(text(insert_sql))
        print('Execution {} inserted into kema_schedule'.format(trigger_message_sid))

    except Exception as e:
        raise

    conn.close()

if __name__ == '__main__':
    create_tables(drop_table=True)
