# -*- coding: utf-8 -*-
"""
Created on Sat Feb 12 02:25:42 2022

@author: Ken.Chen
"""


import const
import utils
from collections import deque
from BaseStrategy import BaseStrategy


class HedgeFxStrategy(BaseStrategy):
    def __init__(self, session, tickers, fee_rate=0.02):
        super().__init__(session, tickers, fee_rate)
        self.usd_exposure_queue = deque(maxlen=3)
        self.usd_exposure = 0
        self.usd_exposure_ema = 0
        self.usd_exposure_decay = 0.8
    
    def run_algo(self):
        self.algo_hedge_fx()
    
    
    def algo_hedge_fx(self):
        self.log('===== USD hedge algo =====', 1)
        hedge_threshold = 10000
        
        
        self.usd_exposure = int(self.last['RITC'] * self.position['RITC'] \
                            + self.position['USD'])
        self.usd_exposure_queue.append(self.usd_exposure)
        self.usd_exposure_ema = 0.8 * self.usd_exposure_ema + 0.2 * self.usd_exposure
                            
        self.log(f'USD exposure: {self.usd_exposure}', 1)
        
        # if min(self.usd_exposure_queue) > hedge_threshold:
        if self.usd_exposure_ema > hedge_threshold:
            self.log('Trigger sell USD', 1)
            utils.sell(self.session, 'USD', min(self.orderbook['USD']['bid1_size'], abs(self.usd_exposure)))            
            
        # if max(self.usd_exposure_queue) < -hedge_threshold:
        if self.usd_exposure_ema < -hedge_threshold:            
            self.log('Trigger Buy USD', 1)
            utils.buy(self.session, 'USD', min(self.orderbook['USD']['ask1_size'], abs(self.usd_exposure)))
            
        
        