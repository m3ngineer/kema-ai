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

def insert_into_table():
    ''' Insert data into table '''

    user_id = str(page_metrics['id'])

    conn = connect_to_rds()
    # Check if user_id already exists
    query = "SELECT username FROM page_metrics WHERE user_id='{}'".format(user_id)
    query_user_id = conn.execute(query)

    if not query_user_id.fetchall(): # If ID not found
        # Assign variables
        username = page_metrics['username']
        update_time = datetime.now().isoformat()
        bio = page_metrics['biography']#.replace('\n', '')
        video_timeline = page_metrics['edge_felix_video_timeline']
        follows = page_metrics['edge_follow']
        followers = page_metrics['edge_followed_by']
        media_collections = page_metrics['edge_media_collections']
        mutual_followed_by = page_metrics['edge_mutual_followed_by']
        saved_media = page_metrics['edge_saved_media']

        # Insert into table
        insert_sql_page = """INSERT INTO page_metrics
                        (user_id, username, update_time, biography , video_timeline, follows, followers,
                        media_collections, mutual_followed_by, saved_media)
                        VALUES ({}, '{}', '{}', $${}$$, {}, {}, {}, {}, {}, {})
                    """.format(user_id, username, update_time, bio, video_timeline, follows, followers,
                               media_collections, mutual_followed_by, saved_media)

        try:
            conn.execute(text(insert_sql_page))
            print('User {} inserted into post_metrics'.format(user_id))

        except Exception as e:
            raise
    conn.close()
