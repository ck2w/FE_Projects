# -*- coding: utf-8 -*-
"""
Created on Sat Feb 12 01:27:27 2022

@author: Ken.Chen
"""
import const
import utils
import pandas as pd

class BaseStrategy:
    def __init__(self, session, tickers, fee_rate):
        self.session = session
        self.tickers = tickers
        
        self.current_tick = None
        self.fee_rate = fee_rate
        
        self.logging1 = True
        self.logging2 = False
        
        # market
        self.orderbook = {k: 0 for k in tickers}
        self.orderbook_full = {k: {} for k in tickers}
        self.orderbook_aggregate = {k: {} for k in tickers}
        self.last = {k: 0 for k in tickers}
        self.prev_last = {k: 0 for k in tickers}
                
        # alpha signal
        self.buy_sell_pressure = {k: 0 for k in tickers}
        self.spread_width = {k: 0 for k in tickers}
        
        self.trend_ema_decay = 0.9
        self.returns_ema = {k: 0 for k in tickers}
        self.vols_ema = {k: 0 for k in tickers}
        self.trend_ema = {k: 0 for k in tickers}
        
        # position
        self.position = {k: 0 for k in tickers}
        
        self.trading_on = True
        
        self.output_text = ''
        
        
        # tensor
        self.tender = {k: {} for k in tickers}

    
    def run(self):
        tick = self.current_tick        
        if tick == self.update_tick():
            return 
        self.update_orderbook()
        self.update_orderbook_full()
        self.update_last()
        self.update_position()
        self.update_tender()
        
        self.compute_alpha()
        
        if self.trading_on:
            self.run_algo()


    def update_tick(self):
        self.current_tick = utils.get_tick(self.session)
        
        self.log(self.current_tick, 1)
        return self.current_tick    
    
       
    def update_orderbook(self):
        for ticker in self.tickers:
            self.orderbook[ticker] = utils.get_orderbook(self.session, ticker)            
        self.log_orderbook()
    
    
    def update_orderbook_full(self):
        for ticker in self.tickers:
            self.orderbook_full[ticker], self.orderbook_aggregate[ticker] = utils.get_orderbook_full(self.session, ticker)
    
    
    def update_last(self):
        self.prev_last = self.last.copy()
        for ticker in self.tickers:
            self.last[ticker] = utils.get_last(self.session, ticker)
        self.log_last()
    
    def update_position(self):
        for ticker in self.tickers:
            self.position[ticker] = utils.get_position(self.session, ticker)            
        self.log_position()
        
            
    def update_tender(self):        
        # new tenders
        tenders_list = utils.get_tender(self.session)
        if tenders_list:
            for tender in tenders_list:
                ticker = tender['ticker']
                self.tender[ticker] = tender
        
        # print(tenders_list)
        # print(self.tender)
        # expired tenders
        for ticker, tender in self.tender.items():
            if tender:
                if self.current_tick >= tender['expires']:
                    self.tender[ticker] = {}                
        
        self.log_tender()
    
    
    def compute_alpha(self):
        self.log('===== alpha signal =====', 2)
        for ticker in self.tickers:
            bid1_price = self.orderbook[ticker]['bid1_price']
            ask1_price = self.orderbook[ticker]['ask1_price']
            mid_price = self.orderbook[ticker]['mid_price']
            bid1_size = self.orderbook[ticker]['bid1_size']
            ask1_size = self.orderbook[ticker]['ask1_size']
            
            
            self.buy_sell_pressure[ticker] = (bid1_size - ask1_size) / (bid1_size + ask1_size)
            
            self.spread_width[ticker] = (ask1_price - bid1_price) / mid_price
            
            
            if self.prev_last[ticker] == 0:
                rets = 0
            else:
                rets = self.last[ticker] / self.prev_last[ticker] - 1
       
            vols = abs(rets)
                        
            self.returns_ema[ticker] = self.trend_ema_decay * self.returns_ema[ticker] + (1-self.trend_ema_decay) * rets
            self.vols_ema[ticker] = self.trend_ema_decay * self.vols_ema[ticker] + (1-self.trend_ema_decay) * vols
            self.trend_ema[ticker] = self.returns_ema[ticker] / (self.vols_ema[ticker] + 0.00000000000000000001)

            
        # print(self.vols_ema)
        
        self.log(f'buy_sell_pressure\n {pd.Series(self.buy_sell_pressure)}', 2)
        self.log(f'spread_width\n {pd.Series(self.spread_width)}', 2)
    
        
    def compute_vwap(self, ticker, side, target_quantity):
            notional = []
            
            cum_volume = 0
            if side == 'bid':
                prices = sorted(self.orderbook_aggregate[ticker][side].keys(), reverse=True)
            elif side == 'ask':
                prices = sorted(self.orderbook_aggregate[ticker][side].keys())
            else:
                pass
            
            for price in prices:
                if cum_volume + self.orderbook_aggregate[ticker][side][price] > target_quantity:
                    notional.append((target_quantity - cum_volume) * price)
                    break
                else:
                    notional.append(self.orderbook_aggregate[ticker][side][price] * price)
                    cum_volume += self.orderbook_aggregate[ticker][side][price]
            
            vwap = sum(notional) / target_quantity
            return vwap
            
    
    def run_algo(self):
        pass
    
    
    def log_orderbook(self):
        self.log('===== orderbook =====', 1)
        for ticker in self.tickers:            
            self.log(f"{ticker:^4}: {self.orderbook[ticker]['bid1_price']:^7}|{self.orderbook[ticker]['ask1_price']:^7}", 1)
    
    
    def log_position(self):
        self.log('===== position =====', 1)
        for ticker in self.tickers:            
            self.log(f"{ticker:^4}: {self.position[ticker]:.1f}", 1)
    
    
    def log_last(self):
        self.log('===== last =====', 1)
        for ticker in self.tickers:            
            self.log(f"{ticker:^4}: {self.last[ticker]:.4f}", 1)
    
    
    def log_tender(self):
        self.log('===== tender =====', 1)
        for ticker in self.tickers: 
            if self.tender[ticker]:
                self.log(f"{ticker:^4}: {self.tender[ticker]['action']} " \
                         f"{self.tender[ticker]['quantity']}@{self.tender[ticker]['price']}", 1)
    
    
    def log(self, text, level=1):
        if level==1 and self.logging1:
            print(text)
            self.output_text = self.output_text + '\n' + str(text)
        if level==2 and self.logging2:
            print(text)
            self.output_text = self.output_text + '\n' + str(text)
        
        
        
        
        