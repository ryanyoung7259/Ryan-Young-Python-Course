#Lesson #4 Yahooquery Get Intraday Stock Data & Historical Stock Data
    #Real time intraday price data, historical price data, financial statement data, and options data
    #https://github.com/dpguthrie/yahooquery
    #***IMPORTANT SETUP NOTE***
        #In order to get financial data (e.g., income statement, balance sheet, etc.), you need to download chromedriver.exe and put it here:
            #C:\ProgramData\Anaconda3\Scripts
        #You don't need to add the location of chromedriver.exe to your path
#import linecache
import yahooquery
from yahooquery import Ticker
import pandas as pd
import datetime

symbols_list = ['AAPL']
#symbols_list = ['AAPL', 'BMY']
#symbols_list = ['AAPL', 'BMY', 'CRON', 'CSCO', 'FB', 'MLM', 'MSFT', 'NVDA', 'TNK', 'XOM']

#Login
    #You tried hiding username and password in a text file, but kept getting this error
        #selenium.common.exceptions.NoSuchElementException: Message: no such element: Unable to locate element: {"method":"xpath","selector":"//button[@id='login-signin']"}
        #(Session info: headless chrome=83.0.4103.61)
#text_file = r"C:\Users\Ryan\SkyDrive\Desktop\Media\Anaconda\Visual Studio Projects\The Madoff\The Madoff\Yahooquery.txt"
#username = linecache.getline(text_file, 2)
#password = linecache.getline(text_file, 3)

#Yahoo burner account. PLEASE DO NOT USE!
#You don't need username and password for historical price data
#tickers = Ticker(symbols_list, asynchronous=False, max_workers=8)
    #asynchronous: Pass asynchronous=True and requests made with multiple symbols will be made asynchronously. Default is False
        #Asynchronous means sequentially
        #By default yahooquery will fetch data in parallel
    #max_workers: Pass max_workers=<n> and modify how many workers are available to make asynchronous requests. This is only used when asynchronous=True is passed as well. Default is 8
    #proxies: Pass proxies={'http': ..., 'https': ...} to use a proxy when making a request. This is recommended when making asynchronous requests.
    #formatted: Pass formatted=True to receive most numeric data in the following form: 'price': {'raw': 126000000000, 'fmt': '$126B'} Default is False
    #username and password: If you subscribe to Yahoo Finance Premium, pass your username and password. You will be logged in and will now be able to access premium properties / methods. All premium properties / methods begin with p_. Disable two-factor authentication for this to work. You do not need to be logged in to access all other properties and methods.
tickers = Ticker(symbols_list, asynchronous=False, max_workers=8, username='youngryan933@yahoo.com', password='youngryan933_Burner')

#Real time and historical price data
    #https://github.com/dpguthrie/yahooquery/blob/master/README.md#historical-pricing
    #If you fetch data intraday, the final row contains the most recent intraday price (1 minute interval)

tickers_price_history_df1 = tickers.history(period='5y', interval='1d')
    #aapl.history(period='max')
    #aapl.history(start='2019-05-01')  # Default end date is now
    #aapl.history(end='2018-12-31')  # Default start date is 1900-01-01
    #Period options = 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
    #Interval options = 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo

print(tickers_price_history_df1)
type(tickers_price_history_df1)
tickers_price_history_df1.columns


tickers_price_history_df2 = tickers_price_history_df1.reset_index()
open_list = []
high_list = []
low_list = []
close_list = []
adjusted_close_list = []
volume_list = []
dividend_list = []
tickers_price_history_df_list = []
for ticker in symbols_list:
    tickers_price_history_df3 = tickers_price_history_df2[tickers_price_history_df2['symbol'] == f"{ticker}"]
    tickers_price_history_df3.loc[:, 'date'] = pd.to_datetime(tickers_price_history_df3.loc[:, 'date']).dt.date
    tickers_price_history_df4 = tickers_price_history_df3.add_prefix(f"{ticker}_")
    tickers_price_history_df4.drop([f"{ticker}_symbol"], axis=1, inplace=True)
    tickers_price_history_df4.set_index(f"{ticker}_date", inplace=True)
    tickers_price_history_df4.index.rename('date', inplace=True)
    open_list.append(tickers_price_history_df4[f"{ticker}_open"])
    high_list.append(tickers_price_history_df4[f"{ticker}_high"])
    low_list.append(tickers_price_history_df4[f"{ticker}_low"])
    close_list.append(tickers_price_history_df4[f"{ticker}_close"])
    adjusted_close_list.append(tickers_price_history_df4[f"{ticker}_adjclose"])
    volume_list.append(tickers_price_history_df4[f"{ticker}_volume"])
    dividend_list.append(tickers_price_history_df4[f"{ticker}_dividends"])
    tickers_price_history_df_list.append(tickers_price_history_df4)

#Close dataframe
close_df1 = pd.concat(close_list, axis=1)
print(close_df1)

#Combined dataframe
tickers_price_history_df5 = pd.concat(tickers_price_history_df_list, axis=1)
#print(tickers_price_history_df5)

#Get options chain data
    #https://github.com/dpguthrie/yahooquery/blob/master/README.md#options