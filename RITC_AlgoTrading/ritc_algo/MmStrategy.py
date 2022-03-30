# -*- coding: utf-8 -*-
"""
Created on Sun Feb 13 03:59:52 2022

@author: Ken.Chen
"""



import const
import utils
from collections import deque
from BaseStrategy import BaseStrategy

class MmStrategy(BaseStrategy):
    def __init__(self, session, tickers, fee_rate=0.02):
        super().__init__(session, tickers, fee_rate)        
        
        self.position_mm = {k: 0 for k in tickers}
