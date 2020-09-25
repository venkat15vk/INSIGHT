#!/Users/vk/miniconda3/bin/python


'''

Purpose of the program:
-----------------------

1. Connect to IEX Exchange API and Download minute by minute stock price for stocks (list of stocks mentioned in the config/stocks.csv file.
2. Using this data on library ta (stands for Technical Analysis), get the technical indicators based on historical and current stock price/volume etc.
3. Normalize the data using minmaxscaler.
4. Load the result in a csv file for training. This is your train data

'''


# load modules
import ta as ta
import datetime as datetime
from iexfinance.stocks import get_historical_intraday
import pandas as pd

import warnings
warnings.filterwarnings('ignore')



#import local libraries



#declare public variables
#dates = [3,4,5,6,7,10,11,12,13,14]
dates = [13,14,15,16,17]
#dates = [3]
year = 2020
month = 7


consolidated = pd.DataFrame()

# read symbols file
SYMBOLS = pd.read_csv('/Users/vk/Desktop/SchoolAndResearch/INSIGHT/HFT/config/DowStocks.csv')
symbols = SYMBOLS['Symbol'].to_list()



# query IEX Exchange, pass stock and date as arguments



def queryIEXForStockData(stock, date):
    #print (stock, date)
    df = get_historical_intraday(stock, date=date, output_format='pandas')
    #print (df.head())
    df['date'] = df.index
    df['stock'] = stock
    df = ta.add_all_ta_features(df, "marketOpen", "marketHigh", "marketLow", "marketClose", "marketVolume", fillna=True)
    df = df.round(5)  
        
    return (df)
    


if __name__ == '__main__':
    
    for sym in symbols:
        for d in dates:
            date = datetime.datetime(year, month, d)
            print ('processing symbol: ' + str(sym) + ' for date: ' + str(date))
            stockDF = queryIEXForStockData(sym, date)
            consolidated = pd.concat([consolidated,stockDF], axis=0) 
            
    
    
    
    consolidated = consolidated.filter(['date', 'label', 'high', 'low', 'average', 'volume',
       'numberOfTrades',  'open',
       'close', 
        'stock', 'momentum_roc', 'momentum_rsi', 'momentum_stoch', 'trend_aroon_ind',
        'trend_macd', 'trend_macd_signal',
       'trend_macd_diff'])
    
    consolidated.to_csv('/Users/vk/Desktop/SchoolAndResearch/INSIGHT/HFT/data/Week2_StockTestData.csv', index=False)
    
    #pcaResult = PrincipalComponentAnalysis.findPCA(consolidated, .95)
    #pcaResult.to_csv('/Users/vk/Desktop/SchoolAndResearch/INSIGHT/HFT/data/StockPCAData.csv', index=False)
