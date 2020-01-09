# -*- coding: utf-8 -*-
"""
Created on Wed Jan  8 10:44:41 2020

@author: Mikkel Vardinghus
"""

import _thread
from time import time, ctime, sleep
from datetime import datetime
import pytz
import requests

datetime.now().replace(microsecond=0).isoformat()

trigger = True

if trigger:
    _thread.start_new_thread()





#def do_something(threadName, delay):
#    count = 0
#    while count < 5:
#        sleep(delay)
#        count += 1
#        print(f'{threadName}: {ctime(time())}')
#        
#try:
#    if trigger:
#        _thread.start_new_thread(do_something, ("Thread-1", 2,) )
#        _thread.start_new_thread(do_something, ("Thread-2", 4,) )
#except KeyboardInterrupt:
#    print("Lukker ned.")
#except:
#    print("Threading fejlede.")