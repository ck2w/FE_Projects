# -*- coding: utf-8 -*-
"""
Created on Sun Feb 13 03:59:38 2022

@author: Ken.Chen
"""


import const
import utils
from collections import deque
from BaseStrategy import BaseStrategy

class TenderStrategy(BaseStrategy):
    def __init__(self, session, tickers, fee_rate=0.02):
        super().__init__(session, tickers, fee_rate)        
        
        self.position_tender = {k: 0 for k in tickers}
        
        
    def run_algo(self):
        self.algo_tender()  
        
    
    def algo_tender(self):
        # only RITC tenders
        
        self.log('===== Tender algo =====', 1)
        
        duration_threshold = 0
        trade_threshold = 0
        cross_trade_threshold = -0.1
                
        
        tender = self.tender['RITC']
        if tender:
            
            duration = tender['expires'] - self.current_tick
            if duration > duration_threshold:
                tender_price = tender['price']
                tender_quantity = tender['quantity']
                direction = tender['action']
                
                if direction == 'BUY':
                    # check bid vwap   
                    bid_vwap_RITC = self.compute_vwap('RITC', 'bid', tender_quantity)
                    bid_vwap_BULL = self.compute_vwap('BULL', 'bid', tender_quantity)
                    bid_vwap_BEAR = self.compute_vwap('BEAR', 'bid', tender_quantity)                    
                    equivalent_price = (bid_vwap_BULL + bid_vwap_BEAR)/self.orderbook['USD']['mid_price']
                    
                    ritc_spread = bid_vwap_RITC - tender_price - const.TRANSACTION_FEE
                    equivalent_spread = equivalent_price - tender_price - const.TRANSACTION_FEE * 2
                    
                    self.log(direction, 2)
                    self.log(str(tender_price) + ' ' + str(bid_vwap_RITC), 2)
                    self.log(ritc_spread, 2)
                    self.log(equivalent_spread, 2)
                    
                    # RITC take tender
                    
                    if ritc_spread > trade_threshold:
                        utils.accept_tender(self.session, tender['tender_id'])                        
                                                
                        target_trade = {'RITC': -tender_quantity}
                        utils.open_all_position(self.session, target_trade) 
                        
                        
                    # BULL, BEAR take                    
                    
                    elif equivalent_spread > cross_trade_threshold:
                        utils.accept_tender(self.session, tender['tender_id'])
                        
                        self.position_tender['RITC'] += tender_quantity
                        self.position_tender['BULL'] -= tender_quantity
                        self.position_tender['BEAR'] -= tender_quantity
                        
                        target_trade = {'BULL': -tender_quantity,
                                        'BEAR': -tender_quantity}
                        utils.open_all_position(self.session, target_trade)
                        
                    
                if direction == 'SELL':
                    # check ask vwap   
                    ask_vwap_RITC = self.compute_vwap('RITC', 'ask', tender_quantity)
                    ask_vwap_BULL = self.compute_vwap('BULL', 'ask', tender_quantity)
                    ask_vwap_BEAR = self.compute_vwap('BEAR', 'ask', tender_quantity)
                    equivalent_price = (ask_vwap_BULL + ask_vwap_BEAR)/self.orderbook['USD']['mid_price']
                    
                    ritc_spread = tender_price - ask_vwap_RITC - const.TRANSACTION_FEE
                    equivalent_spread = tender_price - equivalent_price - const.TRANSACTION_FEE * 2
                    
                    self.log(direction, 2)
                    self.log(str(tender_price) + ' ' + str(ask_vwap_RITC), 2)
                    self.log(ritc_spread, 2)
                    self.log(equivalent_spread, 2)
                    
                    # RITC take tender
                    
                    if ritc_spread > trade_threshold:
                        utils.accept_tender(self.session, tender['tender_id'])
                                                
                        target_trade = {'RITC': tender_quantity}
                        utils.open_all_position(self.session, target_trade) 
                        
                        
                    # BULL, BEAR take
                    
                    if equivalent_spread > cross_trade_threshold:
                        utils.accept_tender(self.session, tender['tender_id'])
                        
                        self.position_tender['RITC'] -= tender_quantity
                        self.position_tender['BULL'] += tender_quantity
                        self.position_tender['BEAR'] += tender_quantity
                        
                        target_trade = {'BULL': tender_quantity,
                                        'BEAR': tender_quantity}
                        utils.open_all_position(self.session, target_trade)                         
        else:
            return
            
            
        def compute_vwap(ticker, side, target_quantity):
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
            
            
            
            
            
            
        