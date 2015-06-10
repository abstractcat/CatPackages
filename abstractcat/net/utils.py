# -*- coding: utf-8 -*-

__author__ = 'abstractcat'

import os
import subprocess
import time

global network_status
global network_status_check_time

network_status=True
network_status_check_time=time.time()

def check_network_status():
    global network_status
    global network_status_check_time

    current_time=time.time()
    #if network is ok, and checked 1 minute ago, return ok
    if network_status==True and (current_time - network_status_check_time)<60:
        return True
    else:
        print('check network status...')
        fnull = open(os.devnull, 'w')
        res = subprocess.call('ping -n 1 8.8.8.8', shell=True, stdout=fnull, stderr=fnull) == 0
        fnull.close()
        network_status=res
        network_status_check_time=current_time
        return res


def ping(ip):
    fnull = open(os.devnull, 'w')
    res = subprocess.call('ping -n 1 %s' % ip, shell=True, stdout=fnull, stderr=fnull) == 0
    fnull.close()
    return res


def tcping(ip, port):
    fnull = open(os.devnull, 'w')
    res = subprocess.call('tcping -n 2 %s %s' % (ip, port), shell=True, stdout=fnull, stderr=fnull) == 0
    fnull.close()
    return res
