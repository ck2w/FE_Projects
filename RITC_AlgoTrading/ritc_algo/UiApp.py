# -*- coding: utf-8 -*-
"""
Created on Sat Feb 12 13:38:53 2022

@author: Ken.Chen
"""

from tkinter import * 
from tkinter import ttk
from PIL import Image, ImageTk

import signal
import requests
from time import sleep
import utils
import const
import threading


shutdown = False
color_nyu = '#57069C'


class UiApp:
    def __init__(self, master, session, strats):
        self.root = master
        self.session = session
        self.strats = strats
        self.lock = threading.Lock()
        
        self.root.geometry('1000x650+200+200')
        self.root.title('RITC 2022 Algo Trading Control Panel')
        self.root.iconbitmap('nyu-logo.ico')
        self.frm1 = Frame(self.root)
        self.frm2 = Frame(self.root)
        self.frm3 = Frame(self.root)
        self.frm4 = Frame(self.root)
        self.createpage()
        

    def createpage(self):
        menu = Menu(self.root)
        self.root.config(menu=menu)
        filemenu = Menu(menu)
        menu.add_cascade(label='menu1', menu=filemenu)
        
        filemenu.add_command(label='1')
        filemenu.add_command(label='2')
        filemenu.add_command(label='3')
        
        onemenu = Menu(menu)
        menu.add_cascade(label='menu2', menu=onemenu)
        onemenu.add_command(label='1')
        onemenu.add_command(label='2')
        onemenu.add_command(label='3')
       
        
        self.frm1.config(bg=color_nyu, height=500, width=785)
        # Label(self.frm1, text='', fg=color_nyu).place(in_=self.frm1, anchor=NW)        
        self.frm1.place(x=175, y=80)
        
        self.frm2.config(bg=color_nyu, height=500, width=150)
        # Label(self.frm2, text='', fg=color_nyu).place(anchor=NW)
        self.frm2.place(x=20, y=80)
        
        self.frm3.config(bg=color_nyu, height=69, width=940)
        # Label(self.frm3, text='', fg=color_nyu).place(in_=self.frm3, anchor=NW)
        self.frm3.place(x=20, y=5)
        
        self.frm4.config(bg=color_nyu, height=69, width=70)
        Label(self.frm4, text='', fg=color_nyu).place(in_=self.frm4, anchor=NW)        
        self.frm4.place(x=20, y=3)
        
        
        img_gif = PhotoImage(file='nyu-logo.png')
        label_img = Label(self.frm4, image=img_gif)
        label_img.img = img_gif
        label_img.pack()
        
        
        Label(self.frm3, text='RITC 2022 Algo Trading Control Panel',
              fg='white', bg=color_nyu, font='Verdana 15 bold').place(x=300, y=20)
        
        
        
        #### frm2: south-west
        Label(self.frm2, text='Quantity', fg='white', bg=color_nyu, font='Verdana 10 bold').place(x=35, y=30)
        
        self.input_quantity = Entry(self.frm2)
        self.input_quantity.place(x=20, y=50, width=100)
        
        Label(self.frm2, text='Ticker', fg='white', bg=color_nyu, font='Verdana 10 bold').place(x=45, y=80)
        
        self.input_ticker = ttk.Combobox(self.frm2, values=['USD', 'RITC', 'BULL', 'BEAR'])
        self.input_ticker.place(x=20, y=100, width=100)
        
        i = 3
        Button(self.frm2, text='Cancel All', command=self.cancel_all, font='Verdana 10 bold').place(x=20, y=40+i*50, width=100)
        i += 1
        Button(self.frm2, text='Close All', command=self.close_all, font='Verdana 10 bold').place(x=20, y=40+i*50, width=100)
        i += 1
        Button(self.frm2, text='Buy', command=self.buy, font='Verdana 10 bold').place(x=20, y=40+i*50, width=100)
        i += 1
        Button(self.frm2, text='Sell', command=self.sell, font='Verdana 10 bold').place(x=20, y=40+i*50, width=100)
        i += 1
        Button(self.frm2, text='Close', command=self.close, font='Verdana 10 bold').place(x=20, y=40+i*50, width=100)
        
        
        
        
        #### frm1: south-east
        # Label(self.frm1, text='',
        #       fg='red', font='Verdana 10 bold').place(x=100, y=50, height=80, width=400)
        Button(self.frm1, text='1', height=1, width=1).place(x=450, y=450)
        Button(self.frm1, text='2', height=1, width=1).place(x=490, y=450)
        Button(self.frm1, text='3', height=1, width=1).place(x=530, y=450)     
        
        i = 0
        Button(self.frm1, text='Refresh', command=self.get_algo_status, font='Verdana 10 bold').place(x=20, y=20+i*50, width=100)
        
        i += 1
        Label(self.frm1, text='Toggle Algo', fg='white', bg=color_nyu, font='Verdana 10 bold').place(x=20, y=20+i*50)
        Label(self.frm1, text='Algo Trading On', fg='white', bg=color_nyu, font='Verdana 10 bold').place(x=140, y=20+i*50)
        
        
        
        
        i += 1
        Button(self.frm1, text='Arbitrage', command=self.toggle_arb, font='Verdana 10 bold').place(x=20, y=20+i*50, width=100)
        self.arb_status = Label(self.frm1, font='Verdana 10 bold', height=1, width=100)
        self.arb_status.place(x=140, y=20+i*50, width=100)
        
        self.position_status = Label(self.frm1, font='Calibre 10', height=10, width=58, justify='left')
        self.position_status.place(x=260, y=20+i*50)
        
        i += 1        
        Button(self.frm1, text='Hedge', command=self.toggle_hedge, font='Verdana 10 bold').place(x=20, y=20+i*50, width=100)
        self.hedge_status = Label(self.frm1, font='Verdana 10 bold', height=1, width=100)
        self.hedge_status.place(x=140, y=20+i*50, width=100)
        
        i += 1        
        Button(self.frm1, text='Trend', command=self.toggle_trend, font='Verdana 10 bold').place(x=20, y=20+i*50, width=100)
        self.trend_status = Label(self.frm1, font='Verdana 10 bold', height=1, width=100)
        self.trend_status.place(x=140, y=20+i*50, width=100)
        
        i += 1        
        Button(self.frm1, text='Tendor', command=self.toggle_tendor, font='Verdana 10 bold').place(x=20, y=20+i*50, width=100)
        self.tendor_status = Label(self.frm1, font='Verdana 10 bold', height=1, width=100)
        self.tendor_status.place(x=140, y=20+i*50, width=100)
        
        i += 1        
        Button(self.frm1, text='MM', command=self.toggle_mm, font='Verdana 10 bold').place(x=20, y=20+i*50, width=100)
        self.mm_status = Label(self.frm1, font='Verdana 10 bold', height=1, width=100)
        self.mm_status.place(x=140, y=20+i*50, width=100)
            
        
        
    
    def get_algo_status(self):
        self.lock.acquire()
        print(self.strats['portfolio'].trading_on)
        if self.strats['portfolio'].trading_on['arb']:
            self.arb_status['text'] = 'ON'
            self.arb_status['fg'] = 'red'
        else:
            self.arb_status['text'] = 'OFF'
            self.arb_status['fg'] = 'black'
            
            
        if self.strats['portfolio'].trading_on['hedge']:
            self.hedge_status['text'] = 'ON'
            self.hedge_status['fg'] = 'red'
        else:
            self.hedge_status['text'] = 'OFF'
            self.hedge_status['fg'] = 'black'
            
        if self.strats['portfolio'].trading_on['trend']:
            self.trend_status['text'] = 'ON'
            self.trend_status['fg'] = 'red'
        else:
            self.trend_status['text'] = 'OFF'
            self.trend_status['fg'] = 'black'
        
        if self.strats['portfolio'].trading_on['tender']:
            self.tendor_status['text'] = 'ON'
            self.tendor_status['fg'] = 'red'
        else:
            self.tendor_status['text'] = 'OFF'
            self.tendor_status['fg'] = 'black'
            
        if self.strats['portfolio'].trading_on['mm']:
            self.mm_status['text'] = 'ON'
            self.mm_status['fg'] = 'red'
        else:
            self.mm_status['text'] = 'OFF'
            self.mm_status['fg'] = 'black'    
            
        # position
        self.position_status['text'] = 'Position\n' + self.strats['portfolio'].log_position()
        
        self.lock.release()
        
    
    def toggle_arb(self):
        self.lock.acquire()
        self.strats['portfolio'].trading_on['arb'] = not self.strats['portfolio'].trading_on['arb']        
        self.lock.release()
        self.get_algo_status()
        
        
    def toggle_hedge(self):
        self.lock.acquire()
        self.strats['portfolio'].trading_on['hedge'] = not self.strats['portfolio'].trading_on['hedge']        
        self.lock.release()
        self.get_algo_status()
        
        
    def toggle_trend(self):
        self.lock.acquire()
        self.strats['portfolio'].trading_on['trend'] = not self.strats['portfolio'].trading_on['trend']
        self.lock.release()
        self.get_algo_status()
    
    
    def toggle_tendor(self):
        self.lock.acquire()
        self.strats['portfolio'].trading_on['tender'] = not self.strats['portfolio'].trading_on['tender']
        self.lock.release()
        self.get_algo_status()
        
        
    def toggle_mm(self):
        self.lock.acquire()
        self.strats['portfolio'].trading_on['mm'] = not self.strats['portfolio'].trading_on['mm']
        self.lock.release()
        self.get_algo_status()
        
        
    def buy(self):
        
        ticker = self.input_ticker.get()
        quantity = self.input_quantity.get()
        utils.buy(self.session, ticker, quantity)
            
    
    def sell(self):        
        ticker = self.input_ticker.get()
        quantity = self.input_quantity.get()
        utils.sell(self.session, ticker, quantity)
        
        
    def close(self):        
        ticker = self.input_ticker.get()        
        utils.close(self.session, ticker)
        
        
    def cancel_all(self):
        print('trigger cancel all')
        utils.cancel_all(self.session)
        
        
    def close_all(self):
        print('trigger close all')
        utils.close_all(self.session)