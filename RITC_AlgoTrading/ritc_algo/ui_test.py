# -*- coding: utf-8 -*-
"""
Created on Sat Feb 12 09:32:44 2022

@author: Ken.Chen
"""

from tkinter import * 
from tkinter import ttk

import signal
import requests
from time import sleep
import utils
import const
import threading

shutdown = False

from UiApp import UiApp


def run_ui(session):
    root = Tk()            
    app = UiApp(root, session, 0)
    mainloop()
    

def run_print():
    print(3)
    sleep(1)    
    print(4)
    sleep(1)
    

def main():
    with requests.Session() as s:        
        s.headers.update(const.API_KEY)
        
        # if 1 < tick < 300:        
        #     root = Tk()            
        #     app = App(root, s)    
        #     mainloop()
        # else:
        #     print('No trading.')
        
        thread1 = threading.Thread(target=run_ui, args=(s,))
        thread2 = threading.Thread(target=run_print)
        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()
        
            
if __name__ == '__main__':
    signal.signal(signal.SIGINT, utils.signal_handler)
    main()

