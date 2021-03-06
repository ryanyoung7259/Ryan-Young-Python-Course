#Lesson #1: Fetch price data for 1 stock from Alpha Vantage

import pandas as pd
import numpy as np
from alpha_vantage.timeseries import TimeSeries
av_gmail_credentials = TimeSeries(key='YOUR_API_KEY', output_format='pandas')
alpha_vantage_tuple = av_gmail_credentials.get_daily_adjusted(symbol='AAPL', outputsize='full')
#You can uncomment the print() and type() if you wish to see the results
#print(alpha_vantage_tuple)
#type(alpha_vantage_tuple)

#print(alpha_vantage_tuple[0])
#print(alpha_vantage_tuple[1])

alpha_vantage_df1 = alpha_vantage_tuple[0]
#type(alpha_vantage_df1)

#See names of dataframe columns
#print(alpha_vantage_df1.columns)

#Select certain columns to be in a new dataframe
alpha_vantage_df2 = alpha_vantage_df1[['1. open', '2. high', '3. low', '4. close', '6. volume']]
print(alpha_vantage_df2)
