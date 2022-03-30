# -*- coding: utf-8 -*-
"""
Created on Fri Feb 11 20:07:43 2022

@author: Ken.Chen
"""

import const
import signal
from time import sleep

class ApiException(Exception):
    pass


class Order:
    def __init__(self,
                 tick,
                 ticker,
                 trader_id,
                 direction,
                 price,
                 quantity,
                 quantity_filled,
                 quantity_remain,
                 ):
        self.tick = tick
        self.ticker = ticker
        self.trader_id = trader_id
        self.direction = direction
        self.price = price
        self.quantity = quantity
        self.quantity_filled = quantity_filled
        self.quantity_remain = quantity_remain


def signal_handler(signum, frame):
    global shutdown
    signal.signal(signal.SIGNIT, signal.SIG_DFL)


# API functions

def get_tick(session):
    resp = session.get(const.SERVER_ADDRESS+'/case')
    if resp.ok:
        case = resp.json()
        return case['tick']        
    raise ApiException('Authorization error. Please check API key.')


def get_orderbook(session, ticker):
    payload = {'ticker': ticker}
    resp = session.get(const.SERVER_ADDRESS+'/securities/book', params=payload)
    if resp.ok:
        book = resp.json()
        orderbook = {}
        orderbook['bid1_size'] = book['bids'][0]['quantity']
        orderbook['ask1_size'] = book['asks'][0]['quantity']
        orderbook['bid1_price'] = book['bids'][0]['price']
        orderbook['ask1_price'] = book['asks'][0]['price']
        orderbook['mid_price'] = (orderbook['ask1_price'] + orderbook['bid1_price']) / 2
        return orderbook                
    else:                
        raise ApiException('Authorization error. Please check API key.')
        

def get_orderbook_full(session, ticker):
    payload = {'ticker': ticker}
    resp = session.get(const.SERVER_ADDRESS+'/securities/book', params=payload)
    if resp.ok:
        book = resp.json()        
        # all orders
        orderbook = {'bid': {},
                     'ask': {}}
        
        # agrregated size
        orderbook_aggregate = {'bid': {},
                               'ask': {}}
        
        for bid in book['bids']:
            if bid['price'] not in orderbook['bid']:
                orderbook['bid'][bid['price']] = []
                orderbook_aggregate['bid'][bid['price']] = 0
            order = Order(tick=bid['tick'],
                          ticker=bid['ticker'],
                          trader_id=bid['trader_id'],
                          direction=bid['action'],
                          price=bid['price'],
                          quantity=bid['quantity'],
                          quantity_filled=bid['quantity_filled'],
                          quantity_remain=bid['quantity']-bid['quantity_filled'])
            orderbook['bid'][bid['price']].append(order)
            orderbook_aggregate['bid'][bid['price']] += order.quantity_remain
            
        for ask in book['asks']:
            if ask['price'] not in orderbook['ask']:
                orderbook['ask'][ask['price']] = []
                orderbook_aggregate['ask'][ask['price']] = 0
            order = Order(tick=ask['tick'],
                          ticker=ask['ticker'],
                          trader_id=ask['trader_id'],
                          direction=ask['action'],
                          price=ask['price'],
                          quantity=ask['quantity'],
                          quantity_filled=ask['quantity_filled'],
                          quantity_remain=ask['quantity']-ask['quantity_filled'])
            orderbook['ask'][ask['price']].append(order)            
            orderbook_aggregate['ask'][ask['price']] += order.quantity_remain
        
        return orderbook, orderbook_aggregate
    else:                
        raise ApiException('Authorization error. Please check API key.')


def get_last(session, ticker):
    payload = {'ticker': ticker}
    resp = session.get(const.SERVER_ADDRESS+'/securities', params=payload)
    if resp.ok:
        ticker_info = resp.json()        
        return ticker_info[0]['last']
    else:                
        raise ApiException('Authorization error. Please check API key.')


def get_position(session, ticker):
    payload = {'ticker': ticker}
    resp = session.get(const.SERVER_ADDRESS+'/securities', params=payload)
    if resp.ok:
        ticker_info = resp.json()
        return ticker_info[0]['position']
    else:                
        raise ApiException('Authorization error. Please check API key.')


def get_tender(session):
    result = []
    resp = session.get(const.SERVER_ADDRESS+'/tenders')
    if resp.ok:
        tender_info = resp.json()        
        return tender_info
    else:                
        raise ApiException('Authorization error. Please check API key.')


def send_order(session, ticker, order_type, direction, price, quantity):
    order = {'ticker': ticker,
             'type': order_type,
             'quantity': quantity,
             'action': direction,
             }
    if order_type == 'LIMIT':
        order['price'] = price
        
    result = session.post(const.SERVER_ADDRESS+'/orders', params=order)    

    return result.status_code


def buy(session, ticker, quantity):
    return send_order(session, 
                      ticker, 
                      const.API_MARKET, 
                      const.API_BUY, 
                      0,
                      quantity)
    
    
def sell(session, ticker, quantity):
    return send_order(session, 
                      ticker, 
                      const.API_MARKET, 
                      const.API_SELL, 
                      0,
                      quantity)


def close(session, ticker):
    # close market position
    while True:
    
        current_position = get_position(session, ticker)
        orderbook = get_orderbook(session, ticker)
        
        if current_position > 0:
            sell(session, 
                 ticker, 
                 min(abs(current_position), max(min(abs(current_position), orderbook['bid1_size']*0.5), 100)))        
        if current_position < 0:
            buy(session, 
                ticker, 
                min(abs(current_position), max(min(abs(current_position), orderbook['bid1_size']*0.5), 100)))
        else:
            return 
        sleep(0.1)

    
def cancel_all(session, ticker=const.ALL_TICKERS):
    cancel = {'ticker': ticker,
             'all': 1
             }
   
    session.post(const.SERVER_ADDRESS+'/commands/cancel', params=cancel)
    
    
def close_all(session, tickers=const.ALL_TICKERS):
    
    while True:
        close_result = []
        for ticker in tickers:
            current_position = get_position(session, ticker)            
            close_result.append(current_position == 0)
            orderbook = get_orderbook(session, ticker)
            if current_position > 0:
                sell(session, 
                     ticker, 
                     min(abs(current_position), max(min(abs(current_position), orderbook['bid1_size']*0.5), 100)))
                
            if current_position < 0:
                buy(session, 
                    ticker, 
                    min(abs(current_position), max(min(abs(current_position), orderbook['ask1_size']*0.5), 100)))
                
        if all(close_result):
            return                
        sleep(0.1)
    

def close_all_position(session, position, tickers=const.ALL_TICKERS):
    
    while True:
        close_result = []
        for ticker in tickers:
            current_position = position[ticker]
            close_result.append(current_position == 0)
            orderbook = get_orderbook(session, ticker)
            if current_position > 0:
                order_size = min(abs(current_position), max(min(abs(current_position), orderbook['bid1_size']*0.5), 100))
                sell(session, ticker, order_size)
                position[ticker] -= order_size
                
            if current_position < 0:
                order_size = min(abs(current_position), max(min(abs(current_position), orderbook['ask1_size']*0.5), 100))
                buy(session, ticker, order_size)
                position[ticker] += order_size
                
        if all(close_result):
            return                
        sleep(0.1)
        
        
def open_all_position(session, target_trades):
    
    while True:
        execute_result = []
        for ticker, target_trade in target_trades.items():
            target_trade = target_trades[ticker]
            execute_result.append(target_trade == 0)
            orderbook = get_orderbook(session, ticker)
            if target_trade > 0:
                order_size = min(abs(target_trade), 
                                 max(min(abs(target_trade), orderbook['ask1_size']*2), 100), 
                                 10000)
                result = buy(session, ticker, order_size)
                if result == 200:
                    target_trades[ticker] -= order_size
                
            if target_trade < 0:
                order_size = min(abs(target_trade), 
                                 max(min(abs(target_trade), orderbook['bid1_size']*2), 100), 
                                 10000)
                result = sell(session, ticker, order_size)
                if result == 200:                
                    target_trades[ticker] += order_size
                
        if all(execute_result):
            return                
        sleep(0.1)
        
        
def accept_tender(session, tender_id):
    
    params = {'id': tender_id}

    result = session.post(const.SERVER_ADDRESS+'/tenders/'+str(tender_id), params=params)    
    print(result.text)
    
    
    