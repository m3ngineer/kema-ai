import json
from twilio.rest import Client
from datetime import datetime, timedelta

from message import send_msg
from db import update_table, select_from_table, insert_into_table
import conf

def execute_reminder_flow(to, from_, data={}):
    ''' Executes Reminder flow in Twilio to send a reminder checkin text '''

    client = Client(conf.twilio_account_sid, conf.twilio_auth_token)

    execution = client.studio \
                      .flows(conf.twilio_flow_reminder_sid) \
                      .executions \
                      .create(to=to, from_=from_, parameters=data) \

    print('Sent message {}'.format(execution.sid))


def send_reminder(to, from_, data={}):
    ''' Executes thread to check-in on goal progress '''

    account_sid = conf.twilio_account_sid
    auth_token = conf.twilio_auth_token
    client = Client(account_sid, auth_token)

    task, barrier, possibility = data['task'], data['barrier'], data['possibility']
    message = client.messages \
                    .create(
                         body="Hi! I'm checking in on your goal to {}. Have you completed this yet? 1 if YES, 2 if NO.".format(task),
                         from_=from_,
                         to=to,
                     )
    thread_data = {
        'trigger_message_sid': data['trigger_message_sid'],
        'user_phone': to,
        'thread_id': '1',
        'position_id': '1',
    }

    insert_into_table(thread_data, 'kema_thread')

def reminder_node_1(data):

    # Read response
    current_date = datetime.now()
    trigger_message_sid = data['trigger_message_sid']
    trigger_text = data['trigger_text']
    user_phone = data['user_phone']
    from_ = conf.twilio_num_from_

    # Determine actions based on response
    if trigger_text == '1':
        # Update kema_schedule database to end schedule
        trigger_message_sid = data['trigger_message_sid']

        # Select past barrier
        sql = """
            SELECT DISTINCT
                trigger_message_sid, barrier, possibility
            FROM
                kema_schedule
            WHERE user_phone = %s;
        """
        prev_possibility = select_from_table(sql, (user_phone,))
        (_, barrier, possibility) = prev_possibility[0]

        # Update schedule_start to the next week
        strt_nxt_wk = current_date + timedelta(7) - timedelta(days=current_date.isoweekday() % 7)
        sql = '''
            UPDATE kema_schedule
            SET schedule_start = %s,
                update_datetime = %s
            WHERE trigger_message_sid = %s
            '''

        params = (strt_nxt_wk, current_date, trigger_message_sid,)
        update_table(sql, params)

        msg = '''That's great! You're that much closer to the goal you set of: {}. You can do it!'''.format(possibility)
        send_msg(msg, user_phone, from_)

    elif trigger_text == '2':
        msg = '''What is keeping you from completing this task?'''
        send_msg(msg, user_phone, from_)
        thread_id = '1'
        next_position_id = '2'

        # Update position in kema_thread db
        sql = '''
            UPDATE kema_thread
            SET thread_id = %s,
                position_id = %s,
                update_datetime = %s
            WHERE user_phone = %s;
            '''

        params = (thread_id, next_position_id, current_date, user_phone,)
        update_table(sql, params)

        return
    else:
        msg = ''' Sorry I didn't understand that. '''
        send_msg(msg, user_phone, from_)

    # Clear path
    sql = '''
        DELETE FROM kema_thread
        WHERE trigger_message_sid = %s;
        '''
    update_table(sql, (trigger_message_sid,))

def reminder_node_2(data):

    current_date = datetime.now()
    trigger_message_sid = data['trigger_message_sid']
    new_barrier = data['trigger_text']
    user_phone = data['user_phone']
    from_ = conf.twilio_num_from_

    # Select past barrier
    sql = """
        SELECT DISTINCT
            trigger_message_sid, barrier, possibility
        FROM
            kema_schedule
        WHERE user_phone = %s;
    """
    prev_barriers = select_from_table(sql, (user_phone,))
    (trigger_message_sid, prev_barrier, possibility) = prev_barriers[0]

    # Update kema_schedule
    updt_barriers = ','.join([prev_barrier,new_barrier])

    sql = '''
        UPDATE kema_schedule
        SET barrier = %s,
            update_datetime = %s
        WHERE trigger_message_sid = %s;
        '''

    params = (updt_barriers, current_date, trigger_message_sid,)
    update_table(sql, params)

    # Clear path
    sql = '''
        DELETE FROM kema_thread
        WHERE trigger_message_sid = %s;
        '''
    update_table(sql, (trigger_message_sid,))

    msg = ''' Got it! I'll remember that for the future. These are are the things that you said have blocked you from completing this task before: {}. Just remember your possibility:  {}. You can do it!'''.format(prev_barrier, possibility)
    send_msg(msg, user_phone, from_)

def create_reminder(data):
    ''' Thread for setting up a new reminder '''

    current_date = datetime.now()
    trigger_message_sid = data['trigger_message_sid']
    trigger_text = data['trigger_text']
    user_phone = data['user_phone']
    from_ = conf.twilio_num_from_

    # Intro
    msg = '''Hello! Today is going to be a  great one :) What's one thing that you have been putting off or want to accomplish?'''
    send_msg(msg, user_phone, from_)

    thread_data = {
        'trigger_message_sid': trigger_message_sid,
        'user_phone': user_phone,
        'thread_id': '0',
        'position_id': '1',
        'thread_data': json.dumps({'trigger_text': trigger_text})
    }

    insert_into_table(thread_data, 'kema_thread')

def create_node_1(data):

    # Accept answer from create_reminder()
    current_date = datetime.now()
    trigger_message_sid = data['trigger_message_sid']
    trigger_text = data['trigger_text']
    user_phone = data['user_phone']
    from_ = conf.twilio_num_from_
    thread_data = json.dumps({'task': trigger_text})
    thread_id, position_id = ('0', '2')

    sql = '''
        UPDATE kema_thread
        SET
            position_id = %s,
            thread_data = thread_data::jsonb || %s::jsonb,
            update_datetime = %s
        WHERE trigger_message_sid = %s
            AND user_phone = %s
            AND thread_id = %s;
        '''

    params = (position_id, thread_data, current_date, trigger_message_sid, user_phone, thread_id,)
    update_table(sql, params)

    # Barrier
    msg = '''What has been holding you back from completing this? What are you afraid of?'''
    send_msg(msg, user_phone, from_)

def create_node_2(data):

    # Accept answer from create_reminder()
    current_date = datetime.now()
    trigger_message_sid = data['trigger_message_sid']
    trigger_text = data['trigger_text']
    user_phone = data['user_phone']
    from_ = conf.twilio_num_from_
    thread_data = json.dumps({'barrier': trigger_text})
    thread_id, position_id = ('0', '3')

    sql = '''
        UPDATE kema_thread
        SET
            position_id = %s,
            thread_data = thread_data::jsonb || %s::jsonb,
            update_datetime = %s
        WHERE trigger_message_sid = %s
            AND user_phone = %s
            AND thread_id = %s;
        '''

    params = (position_id, thread_data, current_date, trigger_message_sid, user_phone, thread_id,)
    update_table(sql, params)

    # Possibility
    msg = '''What's the consequence of not doing this thing? What possibility are you creating by doing this?'''
    send_msg(msg, user_phone, from_)

def create_node_3(data):

    # Accept answer from create_reminder()
    current_date = datetime.now()
    trigger_message_sid = data['trigger_message_sid']
    trigger_text = data['trigger_text']
    user_phone = data['user_phone']
    from_ = conf.twilio_num_from_
    thread_data = json.dumps({'possibility': trigger_text})
    thread_id, position_id = ('0', '4')

    sql = '''
        UPDATE kema_thread
        SET
            position_id = %s,
            thread_data = thread_data::jsonb || %s::jsonb,
            update_datetime = %s
        WHERE trigger_message_sid = %s
            AND user_phone = %s
            AND thread_id = %s;
        '''

    params = (position_id, thread_data, current_date, trigger_message_sid, user_phone, thread_id,)
    update_table(sql, params)

    # Schedule deadline
    msg = '''I'm so glad that you shared that with me :) Let's set a date for when you will accomplish this task by. When will you commit to doing this?'''
    send_msg(msg, user_phone, from_)

def create_node_4(data):

    # Accept answer from create_reminder()
    current_date = datetime.now()
    trigger_message_sid = data['trigger_message_sid']
    trigger_text = data['trigger_text']
    user_phone = data['user_phone']
    from_ = conf.twilio_num_from_
    thread_data = json.dumps({'schedule_deadline_input': trigger_text})
    thread_id, position_id = ('0', '5')

    sql = '''
        UPDATE kema_thread
        SET
            position_id = %s,
            thread_data = thread_data::jsonb || %s::jsonb,
            update_datetime = %s
        WHERE trigger_message_sid = %s
            AND user_phone = %s
            AND thread_id = %s;
        '''

    params = (position_id, thread_data, current_date, trigger_message_sid, user_phone, thread_id,)
    update_table(sql, params)

    # Schedule period
    msg = '''Great! I can send you weekly reminders before this deadline. What days would you like to be reminded? You can also say weekdays, daily, weekend, etc.'''
    send_msg(msg, user_phone, from_)

def create_node_5(data):

    # Accept answer from create_reminder()
    current_date = datetime.now()
    trigger_message_sid = data['trigger_message_sid']
    trigger_text = data['trigger_text']
    user_phone = data['user_phone']
    from_ = conf.twilio_num_from_
    thread_data = json.dumps({'schedule_period_input': trigger_text})
    thread_id = '0'

    sql = '''
        UPDATE kema_thread
        SET
            thread_data = thread_data::jsonb || %s::jsonb,
            update_datetime = %s
        WHERE trigger_message_sid = %s
            AND user_phone = %s
            AND thread_id = %s;
        '''

    params = (thread_data, current_date, trigger_message_sid, user_phone, thread_id,)
    update_table(sql, params)

    # Update kema_schedule with collected data over course of thread
    # Extract thread data
    sql = '''
        SELECT trigger_message_sid, thread_data FROM kema_thread
        WHERE
            trigger_message_sid = %s
            AND user_phone = %s
            AND thread_id = %s;
        '''
    insert_data = select_from_table(sql, (trigger_message_sid, user_phone, thread_id,))
    (_, thread_insert_data) = insert_data[0]

    thread_insert_data_dict = {
        'trigger_message_sid': trigger_message_sid,
        'user_phone': user_phone,
        'trigger_text': thread_insert_data['trigger_text'],
        'task': thread_insert_data['task'],
        'barrier': thread_insert_data['barrier'],
        'possibility': thread_insert_data['possibility'],
        'schedule_deadline_input': thread_insert_data['schedule_deadline_input'],
        'schedule_period_input': thread_insert_data['schedule_period_input'],
    }

    insert_into_table(thread_insert_data_dict, 'kema_schedule')

    # Confirm Time
    msg = '''Ok! I'll remind you on those days'''
    send_msg(msg, user_phone, from_)

    # Clear path
    sql = '''
        DELETE FROM kema_thread
        WHERE trigger_message_sid = %s;
        '''
    update_table(sql, (trigger_message_sid,))

if __name__ == "__main__":
    to = conf.twilio_num_to
    from_ = conf.twilio_num_from_
    send_reminder(to, from_)
