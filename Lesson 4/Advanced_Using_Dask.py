#Lesson #4 Advanced Using Dask

import dask
import dask.dataframe as dd
from dask.delayed import delayed
import os
import sys
import alpaca_trade_api as alpaca
import pandas as pd

#***NOTE: You will need to launch the Visual Studio debugger in order to run this code. You can't just run it in the Interactive environment (when you press Ctrl+E twice)***

#Finds the directory the .py file is located using relative locations
    #https://stackoverflow.com/questions/7165749/open-file-in-a-relative-location-in-python
#Path to Python script
python_script_path = os.path.dirname(sys.argv[0])

#File path to .csv file
price_data_csv_file_path = python_script_path + "\\Alpaca_Price_Data.csv"

#File path to .parquet file
price_data_parquet_file_path = python_script_path + "\\Alpaca_Price_Data.parquet"

alpaca_credentials = alpaca.REST('YOUR_API_KEY', 'YOUR_SECRET_KEY', api_version='v2')

#symbols_list = ['AAPL']
#symbols_list = ['AAPL', 'BMY', 'CSCO']
symbols_list = ['AAPL', 'BMY', 'CSCO', 'EOG', 'F', 'FB', 'GE', 'MLM', 'MSFT', 'NVDA', 'TNK', 'XOM']

#Note the reason why we can't just use dask to fetch data in parallel from Alpaca is the Alpaca API won't allow us to
alpaca_historical_df1 = alpaca_credentials.get_barset(symbols=symbols_list, timeframe='day', limit=1000).df

#You can increase the speed of your algorithm by loading from disk instead of holding all the data in memory (i.e., RAM). We can save the data as either .csv or .parquet. Computers read .parquet files really efficiently (i.e., fast).

#You will get this error if you don't flatten the multi-index prior to saving as a .parquet file:
    #ValueError: parquet must have string column names

#Merge multi-index column names together into 1 level (i.e., flatten column names)
    #https://stackoverflow.com/questions/45878333/merge-multiindex-columns-together-into-1-level
alpaca_historical_df1.columns = ['_'.join(col) for col in alpaca_historical_df1.columns.values]
alpaca_historical_df2 = alpaca_historical_df1.reset_index()
alpaca_historical_df2['time'] = pd.to_datetime(alpaca_historical_df2['time'], infer_datetime_format=True).dt.date
alpaca_historical_df2.rename(columns={'time': 'Date'}, inplace=True)

#Note that I didn't set the index here like I did in Lesson #3: Fetch price data from Alpaca. I set the index when reading the parquet file with dask.
#alpaca_historical_df3 = alpaca_historical_df2.set_index('Date')

#Export pandas dataframe as a .csv file
alpaca_historical_df2.to_csv(price_data_csv_file_path, header=True, index=True, sep=',', mode='w')

#Export pandas dataframe as a .parquet file
#Note you may get an error when executing this line. We might need to install some additional packages to your conda environment.
alpaca_historical_df2.to_parquet(price_data_parquet_file_path, index=True, engine='auto')

#Ideally you want each CPU core to handle a chunk of the data. All the cores processing data simultaneously is called parallelization. The data gets processed faster.
recommended_chunksize = int(round(len(alpaca_historical_df2)/(os.cpu_count()-1)))

#Load Alpaca_Price_Data.parquet using dask
    #Read from .parquet file using dask
        #https://examples.dask.org/dataframes/01-data-access.html#Read-from-Parquet
    #read_parquet dask API documentation
        #https://docs.dask.org/en/latest/dataframe-api.html#dask.dataframe.read_parquet
#Note you may get an error when executing this line. We might need to install some additional packages to your conda environment.

#I set the index here instead. This way the dask workers know that the Date column should be used as their reference.
alpaca_historical_dask_df1 = dd.read_parquet(price_data_parquet_file_path, 
                                            chunksize=recommended_chunksize, 
                                            engine='fastparquet'
                                            ).set_index('Date'
                                            )
#The line above is equivalent to the following line. However, the line above is easier to read.
#alpaca_historical_dask_df1 = dd.read_parquet(price_data_parquet_file_path, chunksize=recommended_chunksize, engine='fastparquet').set_index('Date')

open_list = []
high_list = []
low_list = []
close_list = []
volume_list = []

for ticker in symbols_list:
    #The mistake in the video was that I was using the pandas method of slicing dataframes instead of the dask method. Again, it's the little things that get you.
    #alpaca_open_historical_dask_df1 = alpaca_historical_dask_df1[alpaca_historical_dask_df1[f"{ticker}_open"]] #Pandas slicing method
    alpaca_open_historical_dask_df1 = alpaca_historical_dask_df1[[f"{ticker}_open"]] #Dask slicing method
    open_list.append(alpaca_open_historical_dask_df1)

alpaca_open_historical_concat_dask_df1 = dd.concat(open_list, axis=1, join='outer')

#Convert dask dataframe back to pandas dataframe
    #https://stackoverflow.com/questions/39008391/how-to-transform-dask-dataframe-to-pd-dataframe
    #https://docs.dask.org/en/latest/dataframe-api.html#dask.dataframe.DataFrame.compute
#Dask compute scheduler
    #https://stackoverflow.com/questions/54823577/dask-read-csv-versus-pandas-read-csv
#Dask compute scheduler threads vs. processes
    #https://stackoverflow.com/questions/51202594/switching-from-multiprocess-to-multithreaded-dask-dataframe
    #https://towardsdatascience.com/speeding-up-your-algorithms-part-4-dask-7c6ed79994ef
#alpaca_open_historical_df1 = alpaca_open_historical_concat_dask_df1.compute()
#alpaca_open_historical_df1 = alpaca_open_historical_concat_dask_df1.compute(scheduler='processes')
alpaca_open_historical_df1 = alpaca_open_historical_concat_dask_df1.compute(scheduler='threads')
