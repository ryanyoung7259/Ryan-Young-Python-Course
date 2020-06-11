#Lesson #2: Fetch price data for multiple stocks from Alpha Vantage (less than 5 stocks though)
#Remember the API call limitation of 5 API calls/minute

import pandas as pd
import numpy as np
from alpha_vantage.timeseries import TimeSeries

#Uncomment the following two lines if you want to see the entire DataFrame
#pd.set_option('display.max_columns', 999)
#pd.set_option('display.max_rows', 50000)

av_gmail_credentials = TimeSeries(key='YOUR_API_KEY', output_format='pandas')

symbols_list = ['AAPL', 'EOG', 'MLM', 'NVDA']

open_list = []
high_list = []
low_list = []
close_list = []
volume_list = []

for ticker in symbols_list:
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
