# -*- coding: utf-8 -*-
"""
Created on Fri Feb 11 17:23:33 2022

@author: Ken.Chen
"""

import signal
import requests
from time import sleep
import utils
import const

import threading

from tkinter import * 
from tkinter import ttk

from UiApp import UiApp

# from EtfArbitrageStrategy import EtfArbitrageStrategy
# from HedgeFxStrategy import HedgeFxStrategy
# from TrendStrategy import TrendStrategy
from PortfolioStrategy import PortfolioStrategy

shutdown = False


def run_ui(session, strats):
    root = Tk()            
    app = UiApp(root, session, strats)
    mainloop()
    

def run_strategy(session, strats):    
        
    tick = strats['portfolio'].update_tick()
    while 0 < tick < 297 and not shutdown:            
        print()
 

        strats['portfolio'].run()
        
        sleep(0.1)
        tick = strats['portfolio'].current_tick
   

def main():
    with requests.Session() as s:        
        s.headers.update(const.API_KEY)
        strats = {}
        
        strats['portfolio'] = PortfolioStrategy(session=s,
                                                tickers=const.ALL_TICKERS,
                                                fee_rate=const.TRANSACTION_FEE
                                                )                            
        
        t1 = threading.Thread(target=run_ui, args=(s, strats,))
        t2 = threading.Thread(target=run_strategy, args=(s, strats,))
        
        t1.setDaemon(True)
        t2.setDaemon(True)
        
        t1.start()
        t2.start()
        
        while True:
            alive = False            
            alive = alive or t1.is_alive()
            alive = alive or t2.is_alive()
            if not alive:
                break
        
        t1.join()
        t2.join()        

            
if __name__ == '__main__':
    signal.signal(signal.SIGINT, utils.signal_handler)
    main()
    
            
            
            
            
            
            
            
            
            
            
            
            
            