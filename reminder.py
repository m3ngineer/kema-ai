from twilio.rest import Client
from datetime import datetime

from message import send_msg
from db import update_table, select_from_table
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
                         body="Hi! I'm checking in on your goal to {}. Have you completed this yet? 1 is yes, 2 if not.".format(task),
                         from_=from_,
                         to=to,
                     )
    thread_data = {
        'user_phone': to,
        'thread_id': '1',
        'position_id': '1',
        'thread_data': data,
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

        sql = '''
            UPDATE kema_schedule
            SET schedule_end = %s,
                update_time = %s
            WHERE trigger_message_sid = %s
            '''

        params = (current_date, current_date, trigger_message_sid,)
        update_table(sql, params)

        msg = '''Got it! Just remember your possibility:  {}. You can do it!'''.format(possibility)
        send_msg(msg, user_phone, from_)

    elif trigger_text == '2':
        msg = '''What is the barrier?'''
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

    msg = ''' Got it! I'll remember that for the future. Just remember your possibility:  {}. You can do it!'''.format(possibility)
    send_msg(msg, user_phone, from_)

if __name__ == "__main__":
    to = conf.twilio_num_to
    from_ = conf.twilio_num_from_
    send_reminder(to, from_)
