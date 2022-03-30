# -*- coding: utf-8 -*-
"""
Created on Sat Feb 12 05:08:24 2022

@author: Ken.Chen
"""


import const
import utils
from collections import deque
from BaseStrategy import BaseStrategy

class TrendStrategy(BaseStrategy):
    def __init__(self, session, tickers, fee_rate=0.02):
        super().__init__(session, tickers, fee_rate)
        self.trend_ema_decay = 0.9
        self.count = 0
        
        self.position_trend = {k: 0 for k in tickers}
    
    def run_algo(self):
        self.algo_trend()
    
    
    def algo_trend(self):
        self.log('===== Trend algo =====', 1)
        self.count += 1
        if self.count < 10:
            return
        open_threshold = 0.3
        open_position = 100000
        
        # for ticker in ['BULL', 'BEAR', 'RITC', 'USD']:
        for ticker in ['BULL', 'BEAR', 'RITC']:
        # for ticker in ['RITC', 'USD']:
            current_position = self.position_trend[ticker]            
                       
            
            if self.trend_ema[ticker] > open_threshold and current_position <= 0:
                if ticker == 'RITC':
                    target_position = int(open_position / self.last[ticker] / self.last['USD'])
                else:
                    target_position = int(open_position / self.last[ticker])
            elif self.trend_ema[ticker] < -open_threshold and current_position >= 0:
                if ticker == 'RITC':
                    target_position = -int(open_position / self.last[ticker] / self.last['USD'])
                else:
                    target_position = -int(open_position / self.last[ticker])
            else:
                continue
            
            if target_position > current_position:
                utils.buy(self.session, ticker, target_position - current_position)                
                
            elif target_position < current_position:
                utils.sell(self.session, ticker, current_position - target_position)
                
            self.position_trend[ticker] = target_position
            
            
            
            