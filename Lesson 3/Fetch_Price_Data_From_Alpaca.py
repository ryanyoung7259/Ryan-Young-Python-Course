#Lesson #3: Fetch price data from Alpaca

import alpaca_trade_api as alpaca
import pandas as pd

#Uncomment the following two lines if you want to see the entire DataFrame
pd.set_option('display.max_columns', 999)
#pd.set_option('display.max_rows', 50000)
pd.set_option('display.max_rows', 10)

alpaca_credentials = alpaca.REST('YOUR_API_KEY', 'YOUR_SECRET_KEY', api_version='v2')

symbols_list = ['AAPL', 'BMY', 'CSCO', 'EOG', 'F', 'FB', 'GE', 'MLM', 'MSFT', 'NVDA', 'TNK', 'XOM']

alpaca_historical_df1 = alpaca_credentials.get_barset(symbols=symbols_list, timeframe='day', limit=1000).df

#Merge multi-index column names together into 1 level (in other words "flatten" the columns)
    #https://stackoverflow.com/questions/45878333/merge-multiindex-columns-together-into-1-level
alpaca_historical_df1.columns = ['_'.join(col) for col in alpaca_historical_df1.columns.values]
alpaca_historical_df2 = alpaca_historical_df1.reset_index()
alpaca_historical_df2['time'] = alpaca_historical_df2['time'].dt.date

alpaca_historical_df2.rename(columns={'time':'Date'}, inplace=True)
alpaca_historical_df3 = alpaca_historical_df2.set_index('Date')

open_list = []
high_list = []
low_list = []
close_list = []
volume_list = []

for ticker in symbols_list:
	#Note that the commented out lines are correct and work with all versions of Python. Starting in Python 3.6, f-strings were introduced and they will likely become more predominant moving forward.
    #alpaca_open_historical_df1 = alpaca_historical_df3.filter(regex=r"^%s_open" % ticker)
    alpaca_open_historical_df1 = alpaca_historical_df3.filter(regex=f"^{ticker}_open")

    #alpaca_high_historical_df1 = alpaca_historical_df3.filter(regex=r"^%s_high" % ticker)
    alpaca_high_historical_df1 = alpaca_historical_df3.filter(regex=f"^{ticker}_high")

    #alpaca_low_historical_df1 = alpaca_historical_df3.filter(regex=r"^%s_low" % ticker)
    alpaca_low_historical_df1 = alpaca_historical_df3.filter(regex=f"^{ticker}_low")

    #alpaca_close_historical_df1 = alpaca_historical_df3.filter(regex=r"^%s_close" % ticker)
    alpaca_close_historical_df1 = alpaca_historical_df3.filter(regex=f"^{ticker}_close")

    #alpaca_volume_historical_df1 = alpaca_historical_df3.filter(regex=r"^%s_volume" % ticker)
    alpaca_volume_historical_df1 = alpaca_historical_df3.filter(regex=f"^{ticker}_volume")

    #Rename column
    alpaca_open_historical_df1.columns = [ticker + '_Open']
    alpaca_high_historical_df1.columns = [ticker + '_High']
    alpaca_low_historical_df1.columns = [ticker + '_Low']
    alpaca_close_historical_df1.columns = [ticker + '_Close']
    alpaca_volume_historical_df1.columns = [ticker + '_Volume']

    #Drop any columns which contain all NaN values from dataframe
        #https://stackoverflow.com/questions/45147100/pandas-drop-column-of-nans
    alpaca_open_historical_df2 = alpaca_open_historical_df1.dropna(axis=1, how='all')
    alpaca_high_historical_df2 = alpaca_high_historical_df1.dropna(axis=1, how='all')
    alpaca_low_historical_df2 = alpaca_low_historical_df1.dropna(axis=1, how='all')
    alpaca_close_historical_df2 = alpaca_close_historical_df1.dropna(axis=1, how='all')
    alpaca_volume_historical_df2 = alpaca_volume_historical_df1.dropna(axis=1, how='all')

    open_list.append(alpaca_open_historical_df2)
    high_list.append(alpaca_high_historical_df2)
    low_list.append(alpaca_low_historical_df2)
    close_list.append(alpaca_close_historical_df2)
    volume_list.append(alpaca_volume_historical_df2)
dfopenhistoricaltemp = pd.concat(open_list, axis=1, sort=True)
dfhighhistoricaltemp = pd.concat(high_list, axis=1, sort=True)
dflowhistoricaltemp = pd.concat(low_list, axis=1, sort=True)
dfclosehistoricaltemp = pd.concat(close_list, axis=1, sort=True)
dfvolumehistoricaltemp = pd.concat(volume_list, axis=1, sort=True)

#Sort dataframe columns from oldest to newest
    #Sort index from oldest to newest (i.e., newest values on bottom of dataframe) use ascending=True
    #Sort index from newest to oldest (i.e., newest values at top of dataframe) use ascending=False
alpaca_iex_df_open_historical = dfopenhistoricaltemp.sort_index(ascending=True)
alpaca_iex_df_high_historical = dfhighhistoricaltemp.sort_index(ascending=True)
alpaca_iex_df_low_historical = dflowhistoricaltemp.sort_index(ascending=True)
alpaca_iex_df_close_historical = dfclosehistoricaltemp.sort_index(ascending=True)
alpaca_iex_df_volume_historical = dfvolumehistoricaltemp.sort_index(ascending=True)

#Rename columns so only the ticker symbols are the column headers
alpaca_iex_df_open_historical.columns = alpaca_iex_df_open_historical.columns.str.replace('_Open', '')
alpaca_iex_df_high_historical.columns = alpaca_iex_df_high_historical.columns.str.replace('_High', '')
alpaca_iex_df_low_historical.columns = alpaca_iex_df_low_historical.columns.str.replace('_Low', '')
alpaca_iex_df_close_historical.columns = alpaca_iex_df_close_historical.columns.str.replace('_Close', '')
alpaca_iex_df_volume_historical.columns = alpaca_iex_df_volume_historical.columns.str.replace('_Volume', '')

print(alpaca_iex_df_close_historical)
