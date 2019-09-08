from sqlalchemy import create_engine
from datetime import datetime

import conf

def connect_to_rds(return_engine=False):
    ''' Connects to RDS and returns connection '''
    engine = create_engine(
            "postgresql://{}:{}@{}/{}".format(
                conf.RDS_user,
                conf.RDS_password,
                conf.RDS_host,
                conf.RDS_db_name,
                )
            )
    if return_engine:
        return engine

    conn = engine.connect()
    return conn

def create_tables(drop_table=False):
    ''' Creates post_metric table in RDS database '''
    conn = connect_to_rds()

    if drop_table:
        try:
            sql = 'DROP TABLE {};'.format(drop_table)
            conn.execute(sql)
            print('table {} dropped'.format(table))
        except:
            pass

    # Create new tables
    create_table_sql  = """
            CREATE TABLE kema_ai (
            trigger_message_sid VARCHAR PRIMARY KEY,
            user_phone VARCHAR,
            trigger_text VARCHAR,
            task VARCHAR,
            barrier VARCHAR,
            possibility VARCHAR,
            scheduled_time_text_input VARCHAR,
            scheduled_time TIMESTAMP,
            update_datetime TIMESTAMP
            );
            """

    conn.execute(create_table_sql)
    print('kema_ai table created.')
    conn.close()

def insert_into_table(data):
    '''
    Insert data from execution flow into table
    data: dict {user_id: str, task: str, barrier: str, possibility: str, schedule:
        str, date: datetime}
    '''

    conn = connect_to_rds()

    # Assign variables
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
    insert_sql = """INSERT INTO page_metrics
                (trigger_message_sid, user_phone, trigger_text
                task, barrier, possibility, scheduled_time_text_input,
                scheduled_time, update_datetime)
                VALUES ({}, {}, {}, {}, {}, {}, {}, {}, {})
                """.format(trigger_message_sid, user_phone, trigger_text,
                    task, barrier, possibility, scheduled_time_text_input,
                    scheduled_time, update_datetime)

    try:
        conn.execute(text(insert_sql))
        print('Execution {} inserted into kema_ai'.format(trigger_message_sid))

    except Exception as e:
        raise

    conn.close()
