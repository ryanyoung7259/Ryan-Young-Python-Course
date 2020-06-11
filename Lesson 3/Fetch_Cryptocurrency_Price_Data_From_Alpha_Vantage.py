#Fetch cryptocurrency price data from Alpha Vantage

import pandas as pd
from alpha_vantage.timeseries import TimeSeries #You don't actually need to import this
from alpha_vantage.cryptocurrencies import CryptoCurrencies

#Notice instead of TimeSeries, we use CryptoCurrencies instead
av_gmail_cryptocurrency_credentials = CryptoCurrencies(key='YOUR_API_KEY', output_format='pandas')

cryptocurrency_list = sorted(['BTC','ETH','LTC','XLM'])

cryptocurrency_open_list = []
cryptocurrency_high_list = []
cryptocurrency_low_list = []
cryptocurrency_close_list = []
cryptocurrency_volume_list = []

for ticker in cryptocurrency_list:
    tupledf1 = av_gmail_cryptocurrency_credentials.get_digital_currency_daily(symbol=ticker, market='USD')
    df1 = tupledf1[0]
    df2 = df1[['1a. open (USD)', '2a. high (USD)', '3a. low (USD)', '4a. close (USD)', '5. volume']]
    df3 = df2.reset_index()

    df3['date'] = pd.to_datetime(df3['date']).dt.strftime('%Y-%m-%d')
    df3.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    df4 = df3.set_index('Date')
    df5 = df4.sort_index(ascending=True)
    df6 = df5.add_prefix(ticker + ' ')

    dfcryptocurrencyopendata = df6[ticker + ' Open']
    dfcryptocurrencyhighdata = df6[ticker + ' High']
    dfcryptocurrencylowdata = df6[ticker + ' Low']
    dfcryptocurrencyclosedata = df6[ticker + ' Close']
    dfcryptocurrencyvolumedata = df6[ticker + ' Volume']

    cryptocurrency_open_list.append(dfcryptocurrencyopendata)
    cryptocurrency_high_list.append(dfcryptocurrencyhighdata)
    cryptocurrency_low_list.append(dfcryptocurrencylowdata)
    cryptocurrency_close_list.append(dfcryptocurrencyclosedata)
    cryptocurrency_volume_list.append(dfcryptocurrencyvolumedata)

df_cryptocurrency_historical_open = pd.concat(cryptocurrency_open_list, axis=1, sort=True)
df_cryptocurrency_historical_high = pd.concat(cryptocurrency_high_list, axis=1, sort=True)
df_cryptocurrency_historical_low = pd.concat(cryptocurrency_low_list, axis=1, sort=True)
df_cryptocurrency_historical_close = pd.concat(cryptocurrency_close_list, axis=1, sort=True)
df_cryptocurrency_historical_volume = pd.concat(cryptocurrency_volume_list, axis=1, sort=True)

#Drop any rows which have NaN values in them
df_cryptocurrency_historical_open.dropna(axis=0, how='any', inplace=True)
df_cryptocurrency_historical_high.dropna(axis=0, how='any', inplace=True)
df_cryptocurrency_historical_low.dropna(axis=0, how='any', inplace=True)
df_cryptocurrency_historical_close.dropna(axis=0, how='any', inplace=True)
df_cryptocurrency_historical_volume.dropna(axis=0, how='any', inplace=True)

print(df_cryptocurrency_historical_close)
