#!/usr/bin/python
import os
import sys
import zipfile
import MySQLdb
from server_info import server_info
import argparse

extension = { 'python': '.py',
              'java': '.java' }
support = { 'python': ['ants.py'],
            'java': ['Ants.java',
                     'Aim.java',
                     'Bot.java'
                     'Ilk.java',
                     'Tile.java'] }

# this path structure should match the php api code
# the worker code uses a different path structure
def submission_dir(submission_id):
    return os.path.join(server_info["submissions_path"], str(submission_id//1000), str(submission_id))
    
def create_test_bot(name, language):
    botpath = os.path.join('..','ants','dist','sample_bots', language)
    bot_filename = os.path.join(botpath, name + extension[language])
    if not os.path.exists(bot_filename):
        print('No {0} bot named {1}'.format(language, name))
        print(bot_filename)
        return False

    
    connection = MySQLdb.connect(host = server_info['db_host'],
                                 user = server_info['db_username'],
                                 passwd = server_info['db_password'],
                                 db = server_info['db_name'])
    cursor = connection.cursor(MySQLdb.cursors.DictCursor)
    
    # get next bot name number
    cursor.execute('''
    select username
    from user
    where username like '%s%%'
    ''' % name)
    bot_id = max([int(row['username'][len(name):])
                 for row in cursor.fetchall()] or [0]) + 1
    
    # create user database entry
    # password is test
    cursor.execute('''
    insert into user
    values (null,'%s%s','$6$rounds=54321$hQd}`.j1e#X&PuN*$D8.wbEp6vwwLoC27GpiGVOFediuAWaGTQ2MPHD64i/bVGxtj0XNeRJeJRKVgDC/uTh.W2m5YoaoA6To1cJ7ZF/',
    '%s%s@ai-contest.com',1,'7b3f9842775fa9c9d489a3714e857580',0,'Test Account',11,current_timestamp(),0,0);
    ''' % (name, bot_id, name, bot_id))
    user_id = cursor.lastrowid
    print('user_id: %s' % user_id)
    
    # create submission entry
    cursor.execute('''
    insert into submission (user_id, version, status, timestamp, language_id)  
    values (%s, 1, 20, current_timestamp(), 6)
    ''' % (user_id))
    submission_id = cursor.lastrowid
    print('submission_id: %s' % submission_id)
    
    connection.commit()
    connection.close()
    
    # create submission file
    bot_dir = submission_dir(submission_id)
    os.mkdir(bot_dir)

    bot_zip_filename = os.path.join(bot_dir, 'entry.zip')
    with zipfile.ZipFile(bot_zip_filename, 'w') as bot_zip:
        bot_zip.write(bot_filename, 'MyBot' + extension[language])
        for filename in support[language]:
            support_filename = os.path.join(botpath, filename)
            if os.path.exists(support_filename):
                bot_zip.write(support_filename, filename)
            else:
                print('No support file {0}'.format(filename))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('name')
    parser.add_argument('language', nargs='?', default='python')
    args = parser.parse_args()

    create_test_bot(args.name, args.language)
        
if __name__ == '__main__':
    main()
    
