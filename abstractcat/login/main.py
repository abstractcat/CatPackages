# -*- coding: utf-8 -*-

__author__ = 'abstractcat'

import time
import requests
import json
from threading import Thread
from abstractcat.net import utils
from abstractcat.login import entry


class CreateEntry(Thread):
    def __init__(self):
        super(CreateEntry, self).__init__()
        self.entry_manager = entry.EntryManager()

    def run(self):
        while True:
            if utils.check_network_status():
                success = self.entry_manager.create_entry()
                print(success)
            else:
                print('network error!')


class CheckEntry(Thread):
    def __init__(self):
        super(CheckEntry, self).__init__()
        self.entry_manager = entry.EntryManager()

    def run(self):
        while True:
            if utils.check_network_status():
                (uname, address, cookie) = self.entry_manager.get_random_entry()
                cookie = eval(cookie)
                url = 'http://weibo.com/aj/v6/mblog/info/big?ajwvr=6&id=3851386494411801&page=1'
                response=requests.get(url,cookies=cookie)
                try:
                    json_data = json.loads(response.content)
                    count=json_data['data']['count']
                    if count==0:
                        raise Exception()
                except Exception as e:
                    print 'remove entry:',uname
                    self.entry_manager.remove_entry(uname)
            else:
                print('network error!')
            time.sleep(10)


if __name__ == '__main__':
    # create entry
    CreateEntry().start()

    # check entry
    CheckEntry().start()
