# -*- coding: utf-8 -*-

__author__ = 'abstractcat'

from abstractcat.login import entry
from abstractcat.login import login
from abstractcat.db import postgres
import time

def start():
    entry_manager = entry.EntryManager()
    while True:
        success = entry_manager.create_entry()
        print(success)
        time.sleep(0.5)

if __name__ == '__main__':
    start()

    '''
    uname='fyawhgccjzif78@chacuo.net'
    pwd='5421641469'
    address='123.125.104.240:80'
    sql = 'INSERT INTO entry values(%s,%s,%s);'

    db = postgres.PostgresConn()
    (cookie, status) = login.create_cookie(uname, pwd, address)
    if status == 0 and db.execute_param(sql, (uname, address, cookie)):
        print('success')
    '''

