#!/usr/bin/env python3

from sqlalchemy import create_engine
import datetime
import time
import os


now = datetime.datetime.now()
engine = create_engine("mysql+pymysql://root:root123!@localhost/INSIGHT")




tradeDate = '2020-08-01'  # which will give the results for 14th
tPlusOneDate = '2020-08-30'

#SVC symbols - HD


excludeSymbol = """
                    'ABCD'
"""

def main(f):
    
    result = time.localtime()
    hour, minute, seconds = result.tm_hour, result.tm_min, result.tm_sec
    timeString = str(hour) + ':' + str(minute) + ':' + str(seconds)
    
    html_header = """

<!DOCTYPE html>
<html>
    
    <head>
        <title>PNL as of %s</title>
        <h1 align="center">Risk and PNL - per strategy</h1>
        <h2 align="center">Trade date range - %s to %s</h1>
        <meta http-equiv="refresh" content="15" >
    </head>

""" %(timeString, tradeDate,tPlusOneDate)

    html_body = "<body>"
    
    
    summary_body = """
        <br/><br/>
        <p align="center"><b>Overall Profit &amp; Loss (by Strategy)</b></p>
        
            <table border=20 align="center" style="width:30%">
                <tr>
                    <th>Strategy</th>
                    <th>PNL (in USD)</th>
                </tr>

        """ 
    
    summary_per_date_body = """
        <br/><br/>
        <p align="center"><b>Overall Profit &amp; Loss (by Strategy, Date)</b></p>
        
            <table border=20 align="center" style="width:30%">
                <tr>
                    <th>Strategy</th>
                    <th>Date</th>
                    <th>PNL (in USD)</th>
                </tr>

        """ 
    
    pnl_body = """
        <br/><br/>
        <p align="center"><b>Profit &amp; Loss (by Strategy, Symbol)</b></p>
        
            <table border=20 align="center" style="width:45%">
                <tr>
                    <th>Strategy</th>
                    <th>Symbol</th> 
                    <th>PNL (in USD)</th>
                </tr>

        """    
    
    txn_body = """

            <br/><br/>
            <p align="center"><b> Transaction Details (by Strategy, Symbol, Side)</b></p>
            <table border=50 align="center" style="width:60%">
                <tr>
                    <th>Strategy</th>
                    <th>Symbol</th> 
                    <th>Side</th>
                    <th>Number of Trades</th>
                    <th>Total Traded Quantity</th>
                    <th>Notional Value</th> 
                </tr>

        """

    html_tail = """
    </body>
</html>
    """
    
    
    
    query_0 = """
        select  
        Strategy,
		Side,
        ROUND(sum(Quantity*Price), 3) as NotionalValue 
    FROM INSIGHT.RealTime_OrderBook 
    where 
    Time between '{START}' and '{END}'
    AND Symbol not in ({EXCLUDE_SYMBOL_LIST})
    group by Strategy, Side
    """.format(START=tradeDate,END=tPlusOneDate,EXCLUDE_SYMBOL_LIST=excludeSymbol)
    
    #print (query_0)

    result_0 = con.execute(query_0)
    
    summary_bought = dict()
    summary_buy = dict()
    
    for row in result_0:
        strategy,side,notional = row[0],row[1],row[2]
        k = str(strategy)
        sum_pnl = 0

        if side == 'S':
            if k in summary_bought:
                sum_pnl = round(notional - summary_buy[k], 2)
                summary_body  +=  str('<tr>')
                summary_body  +=  str('<td>') + str(strategy) + str('</td>')
                summary_body  +=  str('<td>') + str(sum_pnl) + str('</td>')
                summary_body +=  str('</tr>')
                
        else:
            summary_bought[k] = k
            summary_buy[k] = notional     
            
            
        
    summary_body += '</table><p/>'        
    html_body += summary_body
    
    
    
    
    query_01 = """
        select  
            DATE(Time) mydate,
            Strategy,
            Side,
            ROUND(sum(Quantity*Price), 3) as NotionalValue 
        FROM INSIGHT.RealTime_OrderBook 
        where 
            Symbol not in ({EXCLUDE_SYMBOL_LIST})
        group by mydate,Strategy, Side
        Order by Strategy
    
    """ .format(EXCLUDE_SYMBOL_LIST=excludeSymbol)
    

    result_01 = con.execute(query_01)
    summary_per_date_bought = dict()
    summary_per_date_buy = dict()
    
    for row in result_01:
        tdate,strategy,side,notional = row[0],row[1],row[2],row[3]
        k = str(strategy) + ':' + str(tdate)
        sum_per_date_pnl = 0

        
        
        if side == 'S':
            if k in summary_per_date_bought:
                sum_per_date_pnl = round(notional - summary_per_date_buy[k], 2)
                summary_per_date_body  +=  str('<tr>')
                summary_per_date_body  +=  str('<td>') + str(strategy) + str('</td>')
                summary_per_date_body  +=  str('<td>') + str(tdate) + str('</td>')
                summary_per_date_body  +=  str('<td>') + str(sum_per_date_pnl) + str('</td>')
                summary_per_date_body +=  str('</tr>')
                
        else:
            summary_per_date_bought[k] = k
            summary_per_date_buy[k] = notional     
            
            
        
    summary_per_date_body += '</table><p/>'        
    html_body += summary_per_date_body 
    
    
    

    
    query_1 = """
       select  
        Strategy,
        Symbol, 
        Side,
        ROUND(sum(Quantity*Price), 3) as NotionalValue 
    FROM INSIGHT.RealTime_OrderBook 
    where 
    Time between '{START}' and '{END}'
    AND Symbol not in ({EXCLUDE_SYMBOL_LIST})
    group by Strategy, Symbol, Side
    order by Strategy, Symbol, Side 
    """.format(START=tradeDate,END=tPlusOneDate,EXCLUDE_SYMBOL_LIST=excludeSymbol)
    
    result_1 = con.execute(query_1)
    bought = dict()
    buy = dict()
    final_output = dict()
    
    count = 1
    
    for row in result_1:
        
        strategy,symbol,side,notional = row[0],row[1],row[2],row[3]
        k = str(strategy) + str(symbol)
        pnl = 0

        if side == 'S':
            if k in bought:
                pnl = round(notional - buy[k], 2)
                pnl_body  +=  str('<tr>')
                pnl_body  +=  str('<td>') + str(strategy) + str('</td>')
                pnl_body  +=  str('<td>') + str(symbol) + str('</td>')
                pnl_body  +=  str('<td>') + str(pnl) + str('</td>')
                pnl_body +=  str('</tr>')
                
        else:
            bought[k] = k
            buy[k] = notional
            

    pnl_body += '</table><p/>'        
    html_body += pnl_body
    
    
    query_2 = """
    select  
        Strategy,
        Symbol, 
        Side, 
        count(Side) as TotalTransaction,
        sum(Quantity) as TotalTradedQuantity,
        ROUND(sum(Quantity*Price), 3) as NotionalValue 
    FROM INSIGHT.RealTime_OrderBook 
    where 
    Time between '{START}' and '{END}'
    AND Symbol not in ({EXCLUDE_SYMBOL_LIST})
    group by Strategy, Symbol, Side
    order by Strategy, Symbol, Side
    
    """.format(START=tradeDate,END=tPlusOneDate,EXCLUDE_SYMBOL_LIST=excludeSymbol)

    result_2 = con.execute(query_2)

    for row in result_2:
        txn_body +=   str('<tr>')
        txn_body += str('<td>') + str(row[0]) + str('</td>')
        txn_body += str('<td>') + str(row[1]) + str('</td>')
        txn_body += str('<td>') + str(row[2]) + str('</td>')
        txn_body += str('<td>') + str(row[3]) + str('</td>')
        txn_body += str('<td>') + str(row[4]) + str('</td>')
        txn_body += str('<td>') + str(row[5]) + str('</td>')
        txn_body += str('</tr>')
    txn_body += '</table><p/>'

    html_body += txn_body 

    totalString = html_header + html_body + html_tail
    return totalString

    



if __name__ == '__main__':
    
    pnlFile = "/Users/vk/Desktop/SchoolAndResearch/INSIGHT/HFT/log/pnl.html"
    os.remove(pnlFile)  # remove old file
    
    hour = 9
    
    while hour < 22:
        
        con = engine.connect()
        f = open(pnlFile, "w")
        htmlString = main(f)
        f.write(htmlString)
        f.close()

        
        
        result = time.localtime()
        hour, minute, seconds = result.tm_hour, result.tm_min, result.tm_sec
        timeString = str(hour) + ':' + str(minute) + ':' + str(seconds)

        print ('Current time: {} - sleeping 30 seconds before checking the database again for updates...'.format(timeString))
        time.sleep(30)
        
        con.close()

