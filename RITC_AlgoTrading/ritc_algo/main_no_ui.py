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

from EtfArbitrageStrategy import EtfArbitrageStrategy
from HedgeFxStrategy import HedgeFxStrategy
from TrendStrategy import TrendStrategy
from TenderStrategy import TenderStrategy

shutdown = False


def run_strategy(session, strats):    
        
    tick = strats.update_tick()
    while tick > 3 and tick < 297 and not shutdown:            
        print()
 

        strats.run()
        
        sleep(0.1)
        tick = strats.current_tick
   

def main():
    with requests.Session() as s:        
        s.headers.update(const.API_KEY)
        strats_arb = EtfArbitrageStrategy(session=s,
                                          tickers=const.ALL_TICKERS,
                                          fee_rate=const.TRANSACTION_FEE
                                          )
        strats_hedge = HedgeFxStrategy(session=s,
                                       tickers=const.ALL_TICKERS,
                                       fee_rate=const.TRANSACTION_FEE   
                                       )
        strats_trend = TrendStrategy(session=s,
                                     tickers=const.ALL_TICKERS,
                                     fee_rate=const.TRANSACTION_FEE   
                                     )
        strats_tendor = TendorStrategy(session=s,
                                     tickers=const.ALL_TICKERS,
                                     fee_rate=const.TRANSACTION_FEE   
                                     )
                       
        tick = strats_tendor.update_tick()
        # while tick > 0 and tick < 297 and not shutdown:            
        while tick < 297 and not shutdown:            
            print()
     
            # strats_arb.run()
            # strats_trend.run()
            strats_tendor.run()
            
            strats_hedge.run()
            
            sleep(0.5)
            tick = strats_tendor.current_tick

            
if __name__ == '__main__':
    signal.signal(signal.SIGINT, utils.signal_handler)
    main()
    
            
            
            
            
            
            
            
            
            
            
            
            
            