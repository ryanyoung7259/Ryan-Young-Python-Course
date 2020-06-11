#Lesson #2: Fetch price data for more than 5 stocks from Alpha Vantage

import pandas as pd
import numpy as np
from alpha_vantage.timeseries import TimeSeries
import time

#Uncomment the following two lines if you want to see the entire DataFrame
#pd.set_option('display.max_columns', 999)
#pd.set_option('display.max_rows', 50000)

av_gmail_credentials = TimeSeries(key='CZ3CF3EP5MPJFFRZ', output_format='pandas')

symbols_list = ['AAPL', 'BMY', 'CSCO', 'EOG', 'F', 'FB', 'GE', 'MLM', 'MSFT', 'NVDA', 'TNK', 'XOM']
#symbols_list_of_lists = [['AAPL', 'BMY', 'CSCO', 'EOG', 'F'], ['FB', 'GE', 'MLM', 'MSFT', 'NVDA'], 'TNK', 'XOM']

#Examples on how to slice a list
#symbols_list = ['AAPL', 'BMY', 'CSCO', 'EOG', 'F', 'FB', 'GE', 'MLM', 'MSFT', 'NVDA', 'TNK', 'XOM']
#list_slice1 = symbols_list[0:4]
#print(list_slice1)

#list_slice2 = symbols_list[2:7]
#print(list_slice2)

#list_slice3 = symbols_list[0:5]
#print(list_slice3)

#list_slice4 = symbols_list[5:5+5]
#print(list_slice4)

#list_slice5 = symbols_list[10:10+5]
#print(list_slice5)

#Two methods of splitting up symbols_list
#Method 1: Standard for loop (easier to someone to read, but slower than list comprehension)
#symbols_list_of_lists = []
#for x in range(start=0, stop=len(symbols_list), step=5):
#    sub_list = symbols_list[x:x+5]
#    symbols_list_of_lists.append(sub_list)
#print(symbols_list_of_lists)

#Method 2: List comprehension (harder for someone to read, but faster than the standard for loop)
symbols_list_of_lists = [symbols_list[x:x+5] for x in range(0, len(symbols_list), 5)]

open_list = []
high_list = []
low_list = []
close_list = []
volume_list = []

for sub_list in symbols_list_of_lists:
    for ticker in sub_list:
        alpha_vantage_tuple = av_gmail_credentials.get_daily_adjusted(symbol=ticker, outputsize='full')
        alpha_vantage_df1 = alpha_vantage_tuple[0]
        alpha_vantage_df2 = alpha_vantage_df1[['1. open', '2. high', '3. low', '4. close', '6. volume']]

        alpha_vantage_df3 = alpha_vantage_df2.reset_index()

        #Make sure the index of dataframe alpha_vantage_df3 is type datetime
        alpha_vantage_df3['date'] = pd.to_datetime(alpha_vantage_df3['date'], infer_datetime_format=True)

        alpha_vantage_df3.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']

        alpha_vantage_df4 = alpha_vantage_df3.set_index('Date')

        alpha_vantage_df5 = alpha_vantage_df4.sort_index(ascending=True)

        alpha_vantage_df6 = alpha_vantage_df5.add_prefix(ticker + '_')

        alpha_vantage_df_open_historical_data = alpha_vantage_df6[ticker + '_Open']

        alpha_vantage_df_high_historical_data = alpha_vantage_df6[ticker + '_High']

        alpha_vantage_df_low_historical_data = alpha_vantage_df6[ticker + '_Low']

        alpha_vantage_df_close_historical_data = alpha_vantage_df6[ticker + '_Close']

        alpha_vantage_df_volume_historical_data = alpha_vantage_df6[ticker + '_Volume']

        #Rename Series to ticker symbol
        alpha_vantage_df_open_historical_data.rename(ticker)
        alpha_vantage_df_high_historical_data.rename(ticker)
        alpha_vantage_df_low_historical_data.rename(ticker)
        alpha_vantage_df_close_historical_data.rename(ticker)
        alpha_vantage_df_volume_historical_data.rename(ticker)

        open_list.append(alpha_vantage_df_open_historical_data)
        high_list.append(alpha_vantage_df_high_historical_data)
        low_list.append(alpha_vantage_df_low_historical_data)
        close_list.append(alpha_vantage_df_close_historical_data)
        volume_list.append(alpha_vantage_df_volume_historical_data)
    time.sleep(61)

df_open_historical = pd.concat(open_list, axis=1, sort=True)
df_high_historical = pd.concat(high_list, axis=1, sort=True)
df_low_historical = pd.concat(low_list, axis=1, sort=True)
df_close_historical = pd.concat(close_list, axis=1, sort=True)
df_volume_historical = pd.concat(volume_list, axis=1, sort=True)

#Drop any rows which have NaN values in them
df_open_historical.dropna(axis=0, how='any', inplace=True)
df_high_historical.dropna(axis=0, how='any', inplace=True)
df_low_historical.dropna(axis=0, how='any', inplace=True)
df_close_historical.dropna(axis=0, how='any', inplace=True)
df_volume_historical.dropna(axis=0, how='any', inplace=True)

print(df_close_historical)
