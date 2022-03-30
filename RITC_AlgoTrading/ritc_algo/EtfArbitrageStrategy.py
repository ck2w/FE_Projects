# -*- coding: utf-8 -*-
"""
Created on Sat Feb 12 01:31:43 2022

@author: Ken.Chen
"""
import const
import utils
import math
from time import sleep
from BaseStrategy import BaseStrategy


class EtfArbitrageStrategy(BaseStrategy):
    def __init__(self, session, tickers, fee_rate=0.02):
        super().__init__(session, tickers, fee_rate)  
        self.net_trigger = 0
        
        self.position_arb = {k: 0 for k in tickers}
        
    
    def run_algo(self):
        self.algo_arbitrage_revert()  
        
    
    def algo_arbitrage_revert(self):
        # trade trend
        
        self.log('===== ETF arbitrage algo =====', 1)
        
        ## parameters
        orignal_trigger_threshold = 0.04
        trigger_threshold = orignal_trigger_threshold + abs(self.net_trigger) * 0.02
        trigger_firstlayersize = 800
        buy_sell_pressures_pressure_threshold = 0.008
        spread_width_threshold = 0.01
        order_size = 5000  ## * 10
        net_trigger_limit = 4
        
        
        # calculation
        fee = self.fee_rate * 2 + self.fee_rate * 1 * self.orderbook['USD']['bid1_price']
        
        fair_spread = self.orderbook['BULL']['mid_price'] \
                     + self.orderbook['BEAR']['mid_price'] \
                     - self.orderbook['RITC']['mid_price'] \
                     * self.orderbook['USD']['mid_price']
        
        
        pos_crossspread_loss = (self.orderbook['BULL']['ask1_price'] - self.orderbook['BULL']['mid_price']) \
                               + (self.orderbook['BEAR']['ask1_price'] - self.orderbook['BEAR']['mid_price']) \
                               + (self.orderbook['RITC']['mid_price'] - self.orderbook['RITC']['bid1_price']) * self.orderbook['USD']['mid_price']
                     
                        
        neg_crossspread_loss = (self.orderbook['BULL']['mid_price'] - self.orderbook['BULL']['bid1_price']) \
                               + (self.orderbook['BEAR']['mid_price'] - self.orderbook['BEAR']['bid1_price']) \
                               + (self.orderbook['RITC']['ask1_price'] - self.orderbook['RITC']['mid_price']) * self.orderbook['USD']['mid_price']
        
        ## positive: buy 1 BULL, buy 1 BEAR, sell 1 RITC
        pos_spread = fair_spread - pos_crossspread_loss - neg_crossspread_loss - fee
        
        ## negative: sell 1 BULL, sell 1 BEAR, buy 1 RITC
        neg_spread = -fair_spread - pos_crossspread_loss - neg_crossspread_loss - fee
        
        self.log(f'pos spread: {pos_spread:.2f}', 1)
        self.log(f'neg spread: {neg_spread:.2f}', 1)
        self.log(f'net trigger: {self.net_trigger}', 1)
        self.log(f'crossspread_loss: {pos_crossspread_loss:.2f}')
        
        
        
        if pos_spread > trigger_threshold and self.net_trigger < net_trigger_limit:
            condition_list = []
            # layer size
            # condition_list.append(self.orderbook['BULL']['bid1_size'] > trigger_firstlayersize)
            # condition_list.append(self.orderbook['BEAR']['bid1_size'] > trigger_firstlayersize)
            # condition_list.append(self.orderbook['RITC']['ask1_size'] > trigger_firstlayersize)
            # bs pressure
            # condition_list.append(self.buy_sell_pressure['BULL'] < -buy_sell_pressures_pressure_threshold)
            # condition_list.append(self.buy_sell_pressure['BEAR'] < -buy_sell_pressures_pressure_threshold)
            # condition_list.append(self.buy_sell_pressure['RITC'] > buy_sell_pressures_pressure_threshold)
            # spread width
            # condition_list.append(max(self.spread_width.values()) < spread_width_threshold)
            if all(condition_list):
                    
                self.log('trigger pos arbitrage', 1)
                
                self.net_trigger += 1
                # send_order_size = int(math.sqrt(1 + abs(self.net_trigger))) * order_size
                send_order_size = max(abs(self.net_trigger),1) * order_size
                # send_order_size = int(order_size / (abs(self.net_trigger)+1))
                # send_order_size = order_size
                
                utils.sell(self.session, 'BULL', send_order_size)
                utils.sell(self.session, 'BEAR', send_order_size)
                utils.buy(self.session, 'RITC', send_order_size)  
                
                self.position_arb['BULL'] -= send_order_size
                self.position_arb['BEAR'] -= send_order_size
                self.position_arb['RITC'] += send_order_size
        
        if neg_spread > trigger_threshold and self.net_trigger > -net_trigger_limit:
            condition_list = []
            # layer size
            # condition_list.append(self.orderbook['BULL']['ask1_size'] > trigger_firstlayersize)
            # condition_list.append(self.orderbook['BEAR']['ask1_size'] > trigger_firstlayersize)
            # condition_list.append(self.orderbook['RITC']['bid1_size'] > trigger_firstlayersize)
            # bs pressure
            # condition_list.append(self.buy_sell_pressure['BULL'] > buy_sell_pressures_pressure_threshold)
            # condition_list.append(self.buy_sell_pressure['BEAR'] > buy_sell_pressures_pressure_threshold)
            # condition_list.append(self.buy_sell_pressure['RITC'] < -buy_sell_pressures_pressure_threshold)
            # spread width
            # condition_list.append(max(self.spread_width.values()) < spread_width_threshold)
            if all(condition_list):
                
                self.log('trigger neg arbitrage', 1)

                self.net_trigger -= 1
                # send_order_size = int(math.sqrt(1 + abs(self.net_trigger))) * order_size
                send_order_size = max(abs(self.net_trigger),1) * order_size
                # send_order_size = int(order_size / (abs(self.net_trigger)+1))
                # send_order_size = order_size
                
                utils.buy(self.session, 'BULL', send_order_size)
                utils.buy(self.session, 'BEAR', send_order_size)
                utils.sell(self.session, 'RITC', send_order_size)
                
                self.position_arb['BULL'] += send_order_size
                self.position_arb['BEAR'] += send_order_size
                self.position_arb['RITC'] -= send_order_size
        
        # revert close
        stoplimit = pos_crossspread_loss + neg_crossspread_loss + orignal_trigger_threshold
    
        if self.net_trigger > 0 and fair_spread < -stoplimit * 0.8:
            utils.close_all_position(self.session, self.position_arb, ['BULL', 'BEAR', 'RITC'])
            self.net_trigger = 0
        
        if self.net_trigger < 0 and fair_spread > stoplimit * 0.8:
            utils.close_all_position(self.session, self.position_arb, ['BULL', 'BEAR', 'RITC'])
            self.net_trigger = 0
        
        