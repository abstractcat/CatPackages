# -*- coding: utf-8 -*-

__author__ = 'abstractcat'

from abstractcat.db import postgres
from abstractcat.login import login


class EntryManager:
    def __init__(self):
        self.db = postgres.PostgresConn()

    # get an available account from db
    def get_available_account(self):
        sql = 'SELECT uname,pwd FROM account WHERE status=true and uname not in(select uname from entry) ORDER BY RANDOM() limit 1;'
        result = self.db.query(sql)
        if result:
            uname = result[0][0]
            pwd = result[0][1]
            return (uname, pwd)
        else:
            return None

    # get an available proxy from db, return None if failed.
    def get_available_proxy(self):
        sql = 'SELECT address FROM proxy WHERE address not in(select address from entry) ORDER BY RANDOM() limit 1;'
        result = self.db.query(sql)
        if result != []:
            address = result[0][0]
            return address
        else:
            return None

    # get a random entry from db, return None if failed
    def get_random_entry(self):
        sql = 'SELECT uname,address,cookie FROM entry ORDER BY RANDOM() limit 1;'
        result = self.db.query(sql)
        if result != []:
            (uname, address, cookie) = result[0]
            return (uname, address, cookie)
        else:
            return None

    # remove entry
    def remove_entry(self, uname):
        sql = 'DELETE FROM entry WHERE uname=%s;'
        return self.db.execute_param(sql, (uname,))

    # remove proxy
    def remove_proxy(self, address):
        sql = 'DELETE FROM proxy WHERE address=%s;'
        return self.db.execute_param(sql, (address,))

    # create an available, return true if sucess
    def create_entry(self):
        sql = 'INSERT INTO entry values(%s,%s,%s);'

        account = self.get_available_account()
        address = self.get_available_proxy()

        if account is not None and address is not None:
            uname = account[0]
            pwd = account[1]
            (cookie, status) = login.create_cookie(uname, pwd, address)
            if status == 0 and self.db.execute_param(sql, (uname, address, cookie)):
                return True

            # remove proxy address if received a bad request status
            #if status == 1:
            #    print 'proxy address %s removed.' % address
            #    self.remove_proxy(address)

        return False

    def add_accounts(self, fname):
        sql = 'INSERT INTO account values(%s,%s,%s);'
        f = open(fname)
        lines = f.readlines()
        accounts = map(lambda x: x.strip().split('\t'), lines)
        for (uname, pwd) in accounts:
            self.db.execute_param(sql, (uname, pwd, True))
