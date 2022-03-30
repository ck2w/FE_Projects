# -*- coding: utf-8 -*-
"""
Created on Sat Feb 12 14:15:29 2022

@author: Ken.Chen
"""

import pandas as pd
from tabulate import tabulate


import const
import utils
from collections import deque
from BaseStrategy import BaseStrategy
from EtfArbitrageStrategy import EtfArbitrageStrategy
from HedgeFxStrategy import HedgeFxStrategy
from TrendStrategy import TrendStrategy
from TenderStrategy import TenderStrategy
from MmStrategy import MmStrategy

class PortfolioStrategy(EtfArbitrageStrategy, 
                        HedgeFxStrategy,
                        TrendStrategy,
                        TenderStrategy,
                        MmStrategy):
    def __init__(self, session, tickers, fee_rate=0.02):
        super().__init__(session, tickers, fee_rate)
        
        self.trading_on = {}
        self.trading_on['arb'] = False
        self.trading_on['hedge'] = False
        self.trading_on['trend'] = False        
        self.trading_on['tender'] = False
        self.trading_on['mm'] = False           
        
    
    def run_algo(self):
        if self.trading_on['arb']:
            self.algo_arbitrage_revert()        
        
        if self.trading_on['hedge']:
            self.algo_hedge_fx()
            
        if self.trading_on['trend']:
            self.algo_trend()
        
        if self.trading_on['tender']:
            self.algo_tender()
    
    
    def log_position(self):
        self.output_text = ''
        
        self.log('===== position =====', 1)
        for ticker in self.tickers:            
            self.log(f"{ticker:^4}: {self.position[ticker]:.1f}", 1)
        
        self.log('===== position: arb =====', 1)
        for ticker in self.tickers:            
            self.log(f"{ticker:^4}: {self.position_arb[ticker]:.1f}", 1)
        
        self.log('===== position: trend =====', 1)
        for ticker in self.tickers:            
            self.log(f"{ticker:^4}: {self.position_trend[ticker]:.1f}", 1)
            
        df = pd.DataFrame({'Total': self.position, 
                           'Arb': self.position_arb, 
                           'Trend': self.position_trend,
                           'Tendor': self.position_tender,
                           'MM': self.position_mm})
        return tabulate(df, headers='keys', tablefmt="psql")
    
