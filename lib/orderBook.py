#!/usr/bin/env python3

# Author - Venkat Krishnan
#

from sqlalchemy import create_engine
import pandas as pd


engine = create_engine("mysql+pymysql://root:root123!@localhost/INSIGHT")
con = engine.connect()

class OrderBook(object):
    def __init__(self, strategy,datatime,side,qty,symbol,price):
        self.strategy = strategy
        self.datatime = datatime
        self.side = side
        self.qty = qty
        self.symbol = symbol
        self.price = price


    def write_to_book(self):
        my_data = [[self.strategy,self.datatime, self.side, self.qty, self.symbol, self.price]]
        df = pd.DataFrame(my_data, columns=['Strategy','Time', 'Side', 'Quantity', 'Symbol', 'Price'])

        try:
            df.to_sql(name='RealTime_OrderBook', con=con, if_exists='append', index=False)
        except:
            print ('dupes found')
            pass

    #print ('Example below')
    #OrderBook('19:30:00','sell',100,'NFLX',240).write_to_book()
