#!/Users/vk/miniconda3/bin/python

import telnetlib
import json
import pandas as pd

import warnings
import numpy as np
warnings.filterwarnings('ignore')

import pickle
import glob
import re

from collections import defaultdict  # available in Python 2.5 and newer
from sqlalchemy import create_engine


engine = create_engine("mysql+pymysql://root:root123!@localhost/INSIGHT")
con = engine.connect()


def write_to_book(strategy,datatime, side, qty, symbol, price):
    
    print (strategy,datatime,side,qty,symbol,price)
    my_data = [[strategy,datatime, side, qty, symbol, price]]
    df = pd.DataFrame(my_data, columns=['Strategy','Time', 'Side', 'Quantity', 'Symbol', 'Price'])

    try:
        print ('')
        print ("-----------TRADE DETAIL-----------")
        #df.to_sql(name='RealTime_OrderBook', con=con, if_exists='append', index=False)
        print ('-----------------------------------')                    

        
    except:
        print ('Error: Not writing this entry, please check write_to_book routine...')
        pass
        

def listenToMktData_and_executeStrategies(quote_host,quote_port):
        

    orderQty = 100
    prev_last_known_entry = pd.DataFrame()
    
    current_position = defaultdict(int)
    output = pd.DataFrame()
    
    
    tn = telnetlib.Telnet(quote_host,quote_port)
    
    features = ['date','stock', 'label', 'high', 'low', 'average', 'volume', 'numberOfTrades', 'open',  'close', 'momentum_roc', 
            'momentum_rsi', 'momentum_stoch', 'trend_macd']
    
    filterFeatures = ['high', 'low', 'average', 'volume', 'numberOfTrades', 'open',  'close', 'momentum_roc', 
            'momentum_rsi', 'momentum_stoch', 'trend_macd']
    
    while True:
        try:
            line = tn.read_until(b"\n", timeout=5)
            line_dec = line.decode('ASCII')
            all_variables = json.loads(line_dec)


            data = dict()
            dataForReference = dict()

            if len(all_variables) > 1:

                for k,v in all_variables.items():
                    if k in features:
                        if v == "":
                            v = 0
                        if k not in ('stock', 'date', 'label'):
                            v = float(v)
                            data[k] = v
                        dataForReference[k] = v

                currentDF = pd.DataFrame()


                if len(prev_last_known_entry) >= 1:
                    currentEntryUnFiltered = pd.DataFrame(dataForReference, index=[0])

                    current_time = currentEntryUnFiltered['label'][0]
                    stock = currentEntryUnFiltered['stock'][0]
                    tradeDate = currentEntryUnFiltered['date'][0]
                    price = currentEntryUnFiltered['close'][0]

                    if price > 0:
                        currentEntry = currentEntryUnFiltered.filter(filterFeatures)
                        lastEntry = prev_last_known_entry.tail(1)
                        prev_last_known_entry = pd.DataFrame(data, index=[0])
                        currentDF = pd.concat([lastEntry, currentEntry])
                        price = currentEntry['close'][0]
                        ordTime = currentEntryUnFiltered['date'][0]
                        stock = currentEntryUnFiltered['stock'][0]
                        qty = 100

                        rollingDataDiff = currentDF.pct_change()
                        rollingDataDiff = rollingDataDiff.tail(1)
                        rollingDataDiff.replace([np.inf, -np.inf, np.nan], 0.0000001,inplace=True)


                        models = glob.glob('/Users/vk/Desktop/SchoolAndResearch/INSIGHT/HFT/models/ORIGINAL/Rand*pkl')

                        # if retrained models available, use those models
                        retrainedModels = glob.glob('/Users/vk/Desktop/SchoolAndResearch/INSIGHT/HFT/models/RETRAINED/*pkl')
                        if len(retrainedModels) > 0:
                            models = retrainedModels

                        model_result = pd.DataFrame()
                        #print (models)

                        for m in models:
                            mat = re.search('.*\/(.*?).pkl', m)

                            model_name = mat.group(1)
                            loaded_model = pickle.load(open(m, 'rb'))
                            result = loaded_model.predict(rollingDataDiff)

                            #print (model_name, result)

                            signal = result[-1]  # the last element in the list, as signals get appended at the end 

                            if current_position[model_name] == 1:
                                if '3:59 PM' in current_time:
                                    side = 'S'
                                    current_position[model_name] -= 1
                                    write_to_book(model_name,ordTime,side,qty,stock,price)
                                else:
                                    if signal == 0:
                                        side = 'S'
                                        current_position[model_name] -= 1
                                        write_to_book(model_name,ordTime,side,qty,stock,price)
                            elif current_position[model_name] == 0:
                                if signal == 1:
                                    if '3:59 PM' not in current_time:
                                        #print ('i came here to buy')
                                        #print (current_position[model_name])
                                        side = 'B'
                                        current_position[model_name] += 1
                                        write_to_book(model_name,ordTime,side,qty,stock,price)


                        #print (currentDF)

                else:
                    prev_last_known_entry = pd.DataFrame(data, index=[0])
                
        except Exception as e:
            print("No more data available, exiting get_market_data thread -")
            break

        
if __name__ == "__main__":
    listenToMktData_and_executeStrategies('127.0.0.1',9999)


