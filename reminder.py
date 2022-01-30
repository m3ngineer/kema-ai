import json
from twilio.rest import Client
from datetime import datetime, timedelta

from message import send_msg
from db import (update_table, select_from_table, insert_into_table,
    update_thread_position, clear_thread_for_user_phone)
import conf

def execute_reminder_flow(to, from_, data={}):
    ''' Executes Reminder flow in Twilio to send a reminder checkin text '''

    client = Client(conf.twilio_account_sid, conf.twilio_auth_token)

    execution = client.studio \
                      .flows(conf.twilio_flow_reminder_sid) \
                      .executions \
                      .create(to=to, from_=from_, parameters=data) \

    print('Sent message {}'.format(execution.sid))


def set_active_task(task_list):
    for i, task in enumerate(task_list):
        if i == 0:
            task['status'] = 'active'
        else:
            task['status'] = 'dormant'
    return task_list

def send_reminder(to, from_, data={}):
    ''' Executes thread to check-in on goal progress '''

    account_sid = conf.twilio_account_sid
    auth_token = conf.twilio_auth_token
    client = Client(account_sid, auth_token)

    clear_thread_for_user_phone(to)

    if len(data.get('tasks')) > 1:
        # Multiple tasks found
        tasks = '\n  '.join(['{}. {}'.format(i+1, task['task']) for i, task in enumerate(data['tasks'])])
        task_num = 1
        message = client.messages \
                        .create(
                             body="Hi there! I'm checking in on your goals.\n  {}.\nLet's go in order. Have you completed number {} yet?\n\n1 if YES, 2 if NO.".format(tasks, task_num),
                             from_=from_,
                             to=to,
                         )

        data['tasks'] = set_active_task(data['tasks'])
        active_task_data = data['tasks'][0]

        thread_data = {
            'trigger_message_sid': active_task_data['trigger_message_sid'],
            'user_phone': to,
            'thread_id': '1',
            'position_id': '3',
            'thread_data': json.dumps(data)
        }

        insert_into_table(thread_data, 'kema_thread')

    elif len(data.get('tasks')) == 1:
        data = data['tasks'][0]
        task, barrier, possibility = data['task'], data['barrier'], data['possibility']
        message = client.messages \
                        .create(
                             body="Hi there! I'm checking in on your goal to {}. Have you completed this yet? 1 if YES, 2 if NO.".format(task),
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
    else:
        # No data found
        print('No tasks found')
        return

def reminder_node_1(data):
    '''Terminal node accepting accepting response from user on completion of tasks
    Updates schedule or requests input on blocking emotions
    '''

    # Read response
    current_date = datetime.now()
    trigger_message_sid = data['trigger_message_sid']
    trigger_text = data['trigger_text']
    user_phone = data['user_phone']
    from_ = conf.twilio_num_from_

    # Determine actions based on response
    if trigger_text == '1' or trigger_text.lower() in ('yes'):
        # Update kema_schedule database to end schedule
        trigger_message_sid = data['trigger_message_sid']

        # Select past barrier
        sql = """
            SELECT DISTINCT
                trigger_message_sid,
                barrier,
                possibility,
                COUNT(trigger_message_sid) OVER (PARTITION BY user_phone) AS num_task
            FROM
                kema_schedule
            WHERE user_phone = %s
                AND trigger_message_sid = %s;
        """
        prev_possibility = select_from_table(sql, (user_phone, trigger_message_sid,))
        (_, barrier, possibility, num_task) = prev_possibility[0]

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

        msg = '''That's great! You're that much closer to the goal you set of: {}. Would you like me to end this reminder permanently or start again next week?\n1. End permanently\n2.Restart for next week'''.format(possibility)
        send_msg(msg, user_phone, from_)

        # Update position in kema_thread db
        thread_id = '1'
        next_position_id = '5'
        update_thread_position(trigger_message_sid, thread_id=thread_id, position_id=next_position_id, user_phone=user_phone)
        return

    elif trigger_text == '2' or trigger_text.lower() in ('no'):
        msg = '''What is keeping you from completing this task?'''
        send_msg(msg, user_phone, from_)
        thread_id = '1'
        next_position_id = '2'

        # Update position in kema_thread db
        update_thread_position(trigger_message_sid, thread_id=thread_id, position_id=next_position_id, user_phone=user_phone)
        return
    else:
        msg = ''' Sorry I didn't understand that. '''
        send_msg(msg, user_phone, from_)

    # Clear path
    update_thread_position(trigger_message_sid, clear_thread=True)

def reminder_node_2(data):
    '''Terminal node to add a new barrier'''

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
        WHERE user_phone = %s
            AND trigger_message_sid = %s;
    """
    prev_barriers = select_from_table(sql, (user_phone, trigger_message_sid,))
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
    update_thread_position(trigger_message_sid, clear_thread=True)

    msg = ''' Got it! I'll remember that for the future. These are are the things that you said have blocked you from completing this task before: {}. Just remember your possibility:  {}. You can do it!'''.format(prev_barrier, possibility)
    send_msg(msg, user_phone, from_)


def reminder_node_3(data):
    """  Multi-task version of reminder_node_1 """

    # data = {'tasks':[{'user_phone': '123', 'task': 'task1', 'trigger_message_sid': 'sid1', 'status': 'test'}, {'user_phone': '123', 'task': 'task2', 'trigger_message_sid': 'sid2', 'status': 'dormant'}]}

    # Read response
    current_date = datetime.now()
    trigger_message_sid = data['trigger_message_sid']
    trigger_text = data['trigger_text']
    user_phone = data['user_phone']
    from_ = conf.twilio_num_from_
    thread_id = '1'

    # Extract thread_data from kema_thread
    sql = '''
        SELECT trigger_message_sid, thread_data FROM kema_thread
        WHERE
            trigger_message_sid = %s
            AND user_phone = %s
            AND thread_id = %s;
        '''
    thread_data_extract = select_from_table(sql, (trigger_message_sid, user_phone, thread_id,))
    (_, thread_data) = thread_data_extract[0]

    # Determine actions based on response
    if trigger_text == '1' or trigger_text.lower() in ('yes'):
        active_task_data = thread_data['tasks'][0] # TODO: set this to search for active task

        # Update kema_schedule database to end schedule
        # Select task metadata
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
            WHERE trigger_message_sid = %s;
            '''

        params = (strt_nxt_wk, current_date, trigger_message_sid,)
        update_table(sql, params)

        msg = '''That's great! You're that much closer to the goal you set of: {}. You can do it!'''.format(possibility)
        send_msg(msg, user_phone, from_)

    elif trigger_text == '2' or trigger_text.lower() in ('no'):
        msg = '''What is keeping you from completing this task?'''
        send_msg(msg, user_phone, from_)
        thread_id = '1'
        next_position_id = '4'

        # Update position in kema_thread db
        update_thread_position(trigger_message_sid, thread_id=thread_id, position_id=next_position_id, user_phone=user_phone)
        print('updated thread position to ', thread_id, next_position_id)
        return
    else:
        msg = ''' Sorry I didn't understand that. '''
        send_msg(msg, user_phone, from_)
        return

    # Send status check for next task
    if len(thread_data.get('tasks')) > 1:
        thread_data['tasks'] = [thr_datum for thr_datum in thread_data['tasks'] if thr_datum['status'] != 'active']
        thread_data['tasks'] = set_active_task(thread_data['tasks'])
        active_data = thread_data['tasks'][0]
        new_trigger_message_sid = active_data['trigger_message_sid']
        if len(thread_data['tasks']) == 1:
            position_id = '1'
        else:
            position_id = '3'

        # Update kema_thread
        sql = '''
            UPDATE kema_thread
            SET
                trigger_message_sid = %s,
                position_id = %s,
                thread_data = %s,
                update_datetime = %s
            WHERE trigger_message_sid = %s
                AND user_phone = %s
                AND thread_id = %s;
            '''

        params = (new_trigger_message_sid, position_id, json.dumps(thread_data), current_date, trigger_message_sid, user_phone, thread_id,)
        update_table(sql, params)

        # update_thread_position(trigger_message_sid, thread_id='1', position_id=position_id)

        msg = "Have you completed {} yet? 1 if YES, 2 if NO.".format(active_data['task'])
        send_msg(msg, user_phone, from_)


def reminder_node_4(data):
    """  Multi-task version of reminder_node_2: append new barrier """

    # Read response
    current_date = datetime.now()
    trigger_message_sid = data['trigger_message_sid']
    new_barrier = data['trigger_text']
    user_phone = data['user_phone']
    from_ = conf.twilio_num_from_
    thread_id = '1'

    # Extract thread_data from kema_thread
    sql = '''
        SELECT trigger_message_sid, thread_data FROM kema_thread
        WHERE
            trigger_message_sid = %s
            AND user_phone = %s
            AND thread_id = %s;
        '''
    thread_data_extract = select_from_table(sql, (trigger_message_sid, user_phone, thread_id,))
    (_, thread_data) = thread_data_extract[0]

    # Select past barrier
    sql = """
        SELECT DISTINCT
            trigger_message_sid, barrier, possibility
        FROM
            kema_schedule
        WHERE user_phone = %s
    """

     # need to specify trigger_message_sid here?
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

    msg = ''' Got it! I'll remember that for the future. These are are the things that you said have blocked you from completing this task before: {}. Just remember your possibility:  {}. You can do it!'''.format(prev_barrier, possibility)
    send_msg(msg, user_phone, from_)


    # Send status check for next task
    if len(thread_data.get('tasks')) > 1:
        thread_data['tasks'] = [thr_datum for thr_datum in thread_data['tasks'] if thr_datum['status'] != 'active']
        thread_data['tasks'] = set_active_task(thread_data['tasks'])
        active_data = thread_data['tasks'][0]
        new_trigger_message_sid = active_data['trigger_message_sid']

        if len(thread_data['tasks']) == 1:
            position_id = '1'
        else:
            position_id = '3'

        # Update kema_thread
        sql = '''
            UPDATE kema_thread
            SET
                trigger_message_sid = %s,
                position_id = %s,
                thread_data = %s,
                update_datetime = %s
            WHERE trigger_message_sid = %s
                AND user_phone = %s
                AND thread_id = %s;
            '''

        params = (new_trigger_message_sid, position_id, json.dumps(thread_data), current_date, trigger_message_sid, user_phone, thread_id,)
        update_table(sql, params)

        # update_thread_position(trigger_message_sid, thread_id='1', position_id=position_id)
        msg = "Have you completed {} yet? 1 if YES, 2 if NO.".format(active_data['task'])
        send_msg(msg, user_phone, from_)


def reminder_node_5(data):
    '''Terminal node accepting accepting response from user on completion of tasks
    Updates schedule or requests input on blocking emotions
    '''

    # Read response
    current_date = datetime.now()
    trigger_message_sid = data['trigger_message_sid']
    trigger_text = data['trigger_text']
    user_phone = data['user_phone']
    from_ = conf.twilio_num_from_

    # Determine actions based on response
    if trigger_text == '1' or trigger_text.lower() in ('yes') or trigger_text == '2' or trigger_text.lower() in ('no'):
        # Update kema_schedule database to delay schedule
        trigger_message_sid = data['trigger_message_sid']

        # Select past barrier
        sql = """
            SELECT DISTINCT
                trigger_message_sid,
                barrier,
                possibility,
                COUNT(trigger_message_sid) OVER (PARTITION BY user_phone) AS num_task
            FROM
                kema_schedule
            WHERE user_phone = %s
                AND trigger_message_sid = %s;
        """
        prev_possibility = select_from_table(sql, (user_phone, trigger_message_sid,))
        (_, barrier, possibility, num_task) = prev_possibility[0]

        if trigger_text == '1' or trigger_text.lower() in ('yes'):
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

            msg = '''That's great! I'll remind you next week. You're that much closer to the goal you set of: {}. You can do it!'''.format(possibility)
            send_msg(msg, user_phone, from_)

        elif trigger_text == '2' or trigger_text.lower() in ('no'):
            # End schedule permanently
            sql = '''
                UPDATE kema_schedule
                SET schedule_end = schedule_start - INTERVAL '1 DAY',
                    update_datetime = %s
                WHERE trigger_message_sid = %s
                '''

            params = (strt_nxt_wk, current_date, trigger_message_sid,)
            update_table(sql, params)

            msg = '''That's great! You're that much closer to the goal you set of: {}. You can do it!'''.format(possibility)
            send_msg(msg, user_phone, from_)

    else:
        msg = ''' Sorry I didn't understand that. '''
        send_msg(msg, user_phone, from_)

    # Clear path
    update_thread_position(trigger_message_sid, clear_thread=True)

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
    update_thread_position(trigger_message_sid, clear_thread=True)

def retrieve_reminders(data):
    ''' Retrieve active tasks '''

    trigger_message_sid = data['trigger_message_sid']
    trigger_text = data['trigger_text']
    user_phone = data['user_phone']
    from_ = conf.twilio_num_from_
    thread_id = '1'

    # Extract task data
    sql = '''
        SELECT
            trigger_message_sid,
            task,
            RANK() OVER (PARTITION BY user_phone ORDER BY update_datetime DESC) AS ordering
        FROM
            kema_schedule
        WHERE
            user_phone = %s
            AND CURRENT_DATE BETWEEN schedule_start AND schedule_end
        ORDER BY
            ordering ASC
        LIMIT 5;
        '''
    task_list = select_from_table(sql, (user_phone,))

    # Send message with task list
    task_str = '\n  '.join(['{}. {}'.format(task_num, task) for (msg_sid, task, task_num) in task_list])
    msg = """
    Here are your active tasks:\n{}\n0. NONE
    """.format(task_str)
    send_msg(msg, user_phone, from_)

    return task_list


def retrieve_menu(data):
    ''' Retrieve menu of options '''

    user_phone = data['user_phone']
    trigger_message_sid = data['trigger_message_sid']
    from_ = conf.twilio_num_from_

    msg = """Menu\n1.MENU to see options\n2.CREATE to start a new task\n3.DELETE to remove a task\n4.EXIT to restart conversation"""
    send_msg(msg, user_phone, from_)

def delete_reminder(data):
    ''' Deletes a reminder '''

    user_phone = data['user_phone']
    trigger_message_sid = data['trigger_message_sid']
    from_ = conf.twilio_num_from_

    task_list = retrieve_reminders(data)

    # Store data in thread
    thread_data = {
        'trigger_message_sid': trigger_message_sid,
        'user_phone': user_phone,
        'thread_id': '2',
        'position_id': '1',
        'thread_data': json.dumps({'task_list': task_list})
    }

    insert_into_table(thread_data, 'kema_thread')

    msg = """Respond with the number of the task you would like to remove"""
    send_msg(msg, user_phone, from_)

def delete_reminder_node_1(data):
    """Accept response for number of task to remove"""

    current_date = datetime.now()
    trigger_message_sid = data['trigger_message_sid']
    trigger_text = data['trigger_text']
    user_phone = data['user_phone']
    from_ = conf.twilio_num_from_
    thread_id = '2'

    if trigger_text.strip() == '0':
        # User exits delete thread
        return

    # Extract trigger text and match task number to delete
    sql = '''
        SELECT
            trigger_message_sid,
            thread_data
        FROM
            kema_thread
        WHERE
            trigger_message_sid = %s
            AND user_phone = %s
            AND thread_id = %s;
        '''
    thread_data = select_from_table(sql, (trigger_message_sid, user_phone, thread_id,))
    (_, task_list) = thread_data[0]

    task_to_delete = None
    for (msg_sid, task, task_num) in task_list['task_list']:
        if str(task_num) == trigger_text.strip():
            task_to_delete = msg_sid

    if task_to_delete:
        # Delete task
        sql = '''
            UPDATE
                kema_schedule
            SET
                schedule_end = schedule_start - INTERVAL '1 DAY'
            WHERE
                trigger_message_sid = %s
                AND user_phone = %s;
            '''
        update_table(sql, (trigger_message_sid, user_phone,))

        # Send confirmation text
        msg = """The task {} has been deleted""".format(task_to_delete)
        send_msg(msg, user_phone, from_)
    else:
        msg = """Ok no tasks were deleted"""
        send_msg(msg, user_phone, from_)

    # Clear thread
    update_thread_position(trigger_message_sid, clear_thread=True)

if __name__ == "__main__":
    to = conf.twilio_num_to
    from_ = conf.twilio_num_from_
    data = [{'trigger_message_sid': 'test', 'trigger_text': 'list tasks', 'user_phone': '+19148198579', 'task': 'test', 'possibility': 'test', 'barrier': 'test,2,2,2,Time,Time,Time,Time', 'schedule_start': '2022-01-16', 'schedule_end': '2022-03-01', 'schedule_weekdays': '0,1,2,3,4,5,6'}, {'trigger_message_sid': 'SMa126b917d45093ebea2189025edfc8db', 'user_phone': '+19148198579', 'task': 'Writing a health Econ article', 'possibility': 'Becoming a health tech company revolutionary', 'barrier': 'Perfection,Time,Not enough time,Time to do it,Doing too much,Not setting a schedule', 'schedule_start': '2022-01-11', 'schedule_end': '2022-01-31', 'schedule_weekdays': '0,1,2,3,4,5,6'}]
    data = {'user_phone': '+19148198579', 'trigger_text': 'list tasks', 'trigger_message_sid': 'test'}
    # send_reminder(to, from_, data=data)

    retrieve_reminders(data)
