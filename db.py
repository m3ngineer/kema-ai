from sqlalchemy import create_engine

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
            id bigint PRIMARY KEY,
            task VARCHAR,
            barrier VARCHAR,
            possibility VARCHAR,
            scheduled_time_text_input VARCHAR,
            scheduled_time TIMESTAMP,
            update_time TIMESTAMP
            );
            """

    conn.execute(create_table_sql)
    print('kema_ai table created.')
    conn.close()
