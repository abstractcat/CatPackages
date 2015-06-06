# -*- coding: utf-8 -*-

__author__ = 'abstractcat'

from abstractcat.login import entry
import time

def start():
    entry_manager = entry.EntryManager()
    while True:
        success = entry_manager.create_entry()
        print(success)

if __name__ == '__main__':
    start()
    time.sleep(1)