#Generic Trading Algorithm

#We will be using this script for Lesson #5 and beyond

from timeit import default_timer as timer
start_time = timer()
import yahooquery
from yahooquery import Ticker
import pandas as pd
import numpy as np
import datetime
import talib
#Import talib cleanly to avoid "only length-1 arrays can be converted to Python scalars" error
    #https://stackoverflow.com/questions/38777651/ta-lib-python-wrapper-only-length-1-arrays-error
    #In other words, don't do the following...
        #import talib
        #from talib.abstract import *
import progressbar


class Generic_Trading_Algorithm():

    def __init__(self):

###################################################################################################################################
        self.yahoo_query_username = 'YAHOO_EMAIL_ADDRESS'
        self.yahoo_query_password = 'YAHOO_EMAIL_ADDRESS_PASSWORD'
###################################################################################################################################

        #Fetch symbols list of all stocks in the S&P 500
        sp_500_url = "http://www.kibot.com/Files/2/SP_500_Intraday.txt"
        sp_500_csv_df1 = pd.read_csv(sp_500_url, delimiter='\t', header=4, engine='python', usecols=['#','Symbol'])
        sp_500_table_range = sp_500_csv_df1.loc[sp_500_csv_df1['#']=='Delisted:'].index.tolist()
        sp_500_csv_df1 = sp_500_csv_df1.iloc[:sp_500_table_range[0]+1]
        sp_500_csv_df1 = sp_500_csv_df1.drop(sp_500_csv_df1.tail(1).index)
        sp_500_raw_symbols_list = sp_500_csv_df1.iloc[:, 1].tolist()

        #Replace the period in certain stock symbols like BF.B and BRK.B to BF-B and BRK-B because Yahoo Finance uses dashes instead of periods
            #See Error Debugging Example.docx for details
        #Set will remove duplicates
        #List converts the set back into a list dtype
        #Sorted will put the list in alphabetical order
        self.sp_500_symbols_list = sorted(list(set([x.replace(".", "-") for x in sp_500_raw_symbols_list])))

        ##Test symbols list
        #self.sp_500_symbols_list = ['AAPL', 'BMY', 'CRON', 'CSCO', 'FB', 'MLM', 'MSFT', 'NVDA', 'TNK', 'XOM']


    def get_stock_price_data_yahooquery(self, data_history_period: str, data_history_period_interval: str):

        print('Fetching stock price data...')

        #Yahooquery Login
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
        tickers = Ticker(self.sp_500_symbols_list, asynchronous=False, max_workers=8, username=self.yahoo_query_username, password=self.yahoo_query_password)

        #Real time and historical price data
            #https://github.com/dpguthrie/yahooquery/blob/master/README.md#historical-pricing
            #If you fetch data intraday, the final row contains the most recent intraday price (1 minute interval)
            #Ticker.history() parameters
                #aapl.history(period='max')
                #aapl.history(start='2019-05-01') #Default end date is now
                #aapl.history(end='2018-12-31') #Default start date is 1900-01-01
                #Period options = 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
                #Interval options = 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
        tickers_price_history_df_or_dict = tickers.history(period=data_history_period, interval=data_history_period_interval)

        working_symbols_list = []
        open_list = []
        high_list = []
        low_list = []
        close_list = []
        adjusted_close_list = []
        volume_list = []
        dividend_list = []

        print('\n\n')
        pbar = progressbar.ProgressBar()

        #We could use list length in the if else statement, but we are unsure of how long the list has to be before yahooquery returns a dictionary of dataframes instead of a single dataframe we have to split up by rows
        #if len(self.sp_500_symbols_list) <= 10:
        if isinstance(tickers_price_history_df_or_dict, pd.DataFrame):

            tickers_price_history_df1 = tickers_price_history_df_or_dict.reset_index()

            for ticker in pbar(self.sp_500_symbols_list):
                #Try/except error handling
                try:
                    tickers_price_history_df2 = tickers_price_history_df1[tickers_price_history_df1['symbol'] == f"{ticker}"]
                    tickers_price_history_df2.loc[:, 'date'] = pd.to_datetime(tickers_price_history_df2.loc[:, 'date']).dt.date
                    tickers_price_history_df2 = tickers_price_history_df2.add_prefix(f"{ticker}_")
                    tickers_price_history_df2.drop([f"{ticker}_symbol"], axis=1, inplace=True)
                    tickers_price_history_df2.set_index(f"{ticker}_date", inplace=True)
                    tickers_price_history_df2.index.rename('Date', inplace=True)

                    #Try to append the dividend column first so that if a KeyError is raised (stock doesn't offer a dividend), the other lists don't get appended with data
                        #If you don't do this, then the price dataframes (e.g., open_df1, close_df1, etc.) will have duplicate columns
                            #An alternative method is to drop duplicates, but keep the first duplicate after pd.concat()
                    dividend_list.append(tickers_price_history_df2[f"{ticker}_dividends"])

                    #Use working_symbols_list to collect all the working ticker symbols and then use it to update self.sp_500_symbols_list later on in this function
                    working_symbols_list.append(ticker)

                    open_list.append(tickers_price_history_df2[f"{ticker}_open"])
                    high_list.append(tickers_price_history_df2[f"{ticker}_high"])
                    low_list.append(tickers_price_history_df2[f"{ticker}_low"])
                    close_list.append(tickers_price_history_df2[f"{ticker}_close"])
                    adjusted_close_list.append(tickers_price_history_df2[f"{ticker}_adjclose"])
                    volume_list.append(tickers_price_history_df2[f"{ticker}_volume"])
                    #dividend_list.append(tickers_price_history_df2[f"{ticker}_dividends"])

                #If Python encounters a KeyError, don't try to get the dividend data
                    #KeyError
                        #Stocks which don't offer dividends won't have dividend columns and so we have to handle the KeyError using try/except
                except KeyError:
                    #Use working_symbols_list to collect all the working ticker symbols and then use it to update self.sp_500_symbols_list later on in this function
                    working_symbols_list.append(ticker)

                    open_list.append(tickers_price_history_df2[f"{ticker}_open"])
                    high_list.append(tickers_price_history_df2[f"{ticker}_high"])
                    low_list.append(tickers_price_history_df2[f"{ticker}_low"])
                    close_list.append(tickers_price_history_df2[f"{ticker}_close"])
                    adjusted_close_list.append(tickers_price_history_df2[f"{ticker}_adjclose"])
                    volume_list.append(tickers_price_history_df2[f"{ticker}_volume"])

                #If Python encounters a AttributeError, pass over those stocks
                    #AttributeError
                        #Stocks which the algorithm is unable to scrape data for will raised an AttributeError. We will simply skip over those stocks.
                except AttributeError:
                    pass

                #If Python encounters any other type of error, pass over those stocks
                except:
                    pass

        #Whenever we use a longer list like the S&P 500, yahooquery returns a dictionary of dataframes and so we would handle them like so...
        else:
            for ticker in pbar(self.sp_500_symbols_list):
                #Try/except error handling
                try:
                    tickers_price_history_df1 = tickers_price_history_df_or_dict[f"{ticker}"]
                    tickers_price_history_df2 = tickers_price_history_df1.reset_index()
                    tickers_price_history_df2.loc[:, 'index'] = pd.to_datetime(tickers_price_history_df2.loc[:, 'index']).dt.date
                    tickers_price_history_df2.set_index('index', inplace=True)
                    tickers_price_history_df2.index.rename('Date', inplace=True)
                    tickers_price_history_df2 = tickers_price_history_df2.add_prefix(f"{ticker}_")

                    #Try to append the dividend column first so that if a KeyError is raised (stock doesn't offer a dividend), the other lists don't get appended with data
                        #If you don't do this, then the price dataframes (e.g., open_df1, close_df1, etc.) will have duplicate columns
                            #An alternative method is to drop duplicates, but keep the first duplicate after pd.concat()
                    dividend_list.append(tickers_price_history_df2[f"{ticker}_dividends"])

                    #Use working_symbols_list to collect all the working ticker symbols and then use it to update self.sp_500_symbols_list later on in this function
                    working_symbols_list.append(ticker)

                    open_list.append(tickers_price_history_df2[f"{ticker}_open"])
                    high_list.append(tickers_price_history_df2[f"{ticker}_high"])
                    low_list.append(tickers_price_history_df2[f"{ticker}_low"])
                    close_list.append(tickers_price_history_df2[f"{ticker}_close"])
                    adjusted_close_list.append(tickers_price_history_df2[f"{ticker}_adjclose"])
                    volume_list.append(tickers_price_history_df2[f"{ticker}_volume"])
                    #dividend_list.append(tickers_price_history_df2[f"{ticker}_dividends"])

                #If Python encounters a KeyError, don't try to get the dividend data
                    #KeyError
                        #Stocks which don't offer dividends won't have dividend columns and so we have to handle the KeyError using try/except
                except KeyError:
                    #Use working_symbols_list to collect all the working ticker symbols and then use it to update self.sp_500_symbols_list later on in this function
                    working_symbols_list.append(ticker)

                    open_list.append(tickers_price_history_df2[f"{ticker}_open"])
                    high_list.append(tickers_price_history_df2[f"{ticker}_high"])
                    low_list.append(tickers_price_history_df2[f"{ticker}_low"])
                    close_list.append(tickers_price_history_df2[f"{ticker}_close"])
                    adjusted_close_list.append(tickers_price_history_df2[f"{ticker}_adjclose"])
                    volume_list.append(tickers_price_history_df2[f"{ticker}_volume"])

                #If Python encounters a AttributeError, pass over those stocks
                    #AttributeError
                        #Stocks which the algorithm is unable to scrape data for will raised an AttributeError. We will simply skip over those stocks.
                except AttributeError:
                    pass

                #If Python encounters any other type of error, pass over those stocks
                except:
                    pass

        #Update self.sp_500_symbols_list so that it only contains the symbols which we could actually pull data for
        self.sp_500_symbols_list = working_symbols_list

        #Create open, high, low, close, adjusted close, volume, and dividend dataframes
        open_df1 = pd.concat(open_list, axis=1, sort=True)
        high_df1 = pd.concat(high_list, axis=1, sort=True)
        low_df1 = pd.concat(low_list, axis=1, sort=True)
        close_df1 = pd.concat(close_list, axis=1, sort=True)
        adjusted_close_df1 = pd.concat(adjusted_close_list, axis=1, sort=True)
        volume_close_df1 = pd.concat(volume_list, axis=1, sort=True)
        dividend_df1 = pd.concat(dividend_list, axis=1, sort=True)

        print('Fetching stock price data...DONE')

        return open_df1, high_df1, low_df1, close_df1, adjusted_close_df1, volume_close_df1, dividend_df1


    #Simple Moving Average (SMA)
    def calc_sma(self, close_price_dataframe: pd.DataFrame, period: int):

        print(f"Calculating SMA ({period})...")

        sma_list = []

        #You can't use self.sp_500_symbols_list because the column names in close_price_dataframe are different (i.e., AAPL_close instead of AAPL)
            #Technically, you can use self.sp_500_symbols_list since it has been updated using working_symbols_list, but you have to filter the dataframe for the symbols which match prior to using talib.
                #Example
                    #for ticker in self.sp_500_symbols_list:
                    #    close_price_dataframe_filtered = close_price_dataframe.filter(regex=rf"^{ticker}_")
                    #    sma = talib.SMA(np.array(close_price_dataframe_filtered), timeperiod=period)
        #for ticker in self.sp_500_symbols_list:
        for ticker in close_price_dataframe:
            sma = talib.SMA(np.array(close_price_dataframe[ticker]), timeperiod=period)
            #If you didn't want to use np.array, you could just put .values after the column name which will convert it into an array
            #sma = talib.SMA(close_price_dataframe[ticker].values, timeperiod=period)

            sma_list.append(sma)

        #Create DataFrame and reapply the original index
        original_index_list = close_price_dataframe.index.tolist()
        sma_df1 = pd.DataFrame(sma_list).T
        sma_column_list = [x + f'_{period}_sma' for x in self.sp_500_symbols_list]
        sma_df1.columns = sma_column_list
        sma_df1.loc[:, 'Date'] = original_index_list
        sma_df1 = sma_df1.set_index('Date')

        print(f"Calculating SMA ({period})...DONE")

        return sma_df1


    def calc_bollinger_bands(self, close_price_dataframe: pd.DataFrame, timeperiod: int, nbdevup: int, nbdevdn: int, matype: int):

        print(f"Calculating Bollinger Bands ({timeperiod})...")

        upper_bollinger_bands_list = []
        middle_bollinger_bands_list = []
        lower_bollinger_bands_list = []

        #You can't use self.sp_500_symbols_list because the column names in close_price_dataframe are different (i.e., AAPL_close instead of AAPL)
            #Technically, you can use self.sp_500_symbols_list since it has been updated using working_symbols_list, but you have to filter the dataframe for the symbols which match prior to using talib.
                #Example
                    #for ticker in self.sp_500_symbols_list:
                    #    close_price_dataframe_filtered = close_price_dataframe.filter(regex=rf"^{ticker}_")
                    #    sma = talib.SMA(np.array(close_price_dataframe_filtered), timeperiod=period)
        #for ticker in self.sp_500_symbols_list:
        for ticker in close_price_dataframe:
            #TA-Lib matype parameter numbers list
                #TA-Lib uses numbers which correspond to different types of moving averages you can use for a particular technical analysis indicator
                #List of values for the Moving Average Type:
                    #https://www.quantopian.com/posts/macd-exponential-or-weighted
                    #0: SMA (simple)
                    #1: EMA (exponential)
                    #2: WMA (weighted)
                    #3: DEMA (double exponential)
                    #4: TEMA (triple exponential)
                    #5: TRIMA (triangular)
                    #6: KAMA (Kaufman adaptive)
                    #7: MAMA (Mesa adaptive)
                    #8: T3 (triple exponential T3)
            upper_band, middle_band, lower_band = talib.BBANDS(np.array(close_price_dataframe[ticker]), timeperiod=timeperiod, nbdevup=nbdevup, nbdevdn=nbdevdn, matype=matype)

            upper_bollinger_bands_list.append(upper_band)
            middle_bollinger_bands_list.append(middle_band)
            lower_bollinger_bands_list.append(lower_band)

        #Create DataFrame and reapply the original index
        original_index_list = close_price_dataframe.index.tolist()

        #Upper Bollinger Bands
        upper_bollinger_bands_df1 = pd.DataFrame(upper_bollinger_bands_list).T
        upper_bollinger_bands_column_list = [x + f"_{timeperiod}_upper_bollinger_bands" for x in self.sp_500_symbols_list]
        upper_bollinger_bands_df1.columns = upper_bollinger_bands_column_list
        upper_bollinger_bands_df1.loc[:, 'Date'] = original_index_list
        upper_bollinger_bands_df1 = upper_bollinger_bands_df1.set_index('Date')

        #Middle Bollinger Bands
        middle_bollinger_bands_df1 = pd.DataFrame(middle_bollinger_bands_list).T
        middle_bollinger_bands_column_list = [x + f"_{timeperiod}_middle_bollinger_bands" for x in self.sp_500_symbols_list]
        middle_bollinger_bands_df1.columns = middle_bollinger_bands_column_list
        middle_bollinger_bands_df1.loc[:, 'Date'] = original_index_list
        middle_bollinger_bands_df1 = middle_bollinger_bands_df1.set_index('Date')

        #Lower Bollinger Bands
        lower_bollinger_bands_df1 = pd.DataFrame(lower_bollinger_bands_list).T
        lower_bollinger_bands_column_list = [x + f"_{timeperiod}_middle_bollinger_bands" for x in self.sp_500_symbols_list]
        lower_bollinger_bands_df1.columns = lower_bollinger_bands_column_list
        lower_bollinger_bands_df1.loc[:, 'Date'] = original_index_list
        lower_bollinger_bands_df1 = lower_bollinger_bands_df1.set_index('Date')

        print(f"Calculating Bollinger Bands ({timeperiod})...DONE")

        return upper_bollinger_bands_df1, middle_bollinger_bands_df1, lower_bollinger_bands_df1


    def strategy_sma_crossover(self, short_term_sma_dataframe: pd.DataFrame, long_term_sma_dataframe: pd.DataFrame, short_term_moving_average: int, long_term_moving_average: int, sma_moving_average_lookback_time_period: int):

        print('Analyzing Simple Moving Average Strategy...')

        #Find stocks in which the short term moving average has crossed above the long term moving average within the most recent 20 days
        short_term_sma_dataframe = short_term_sma_dataframe.tail(sma_moving_average_lookback_time_period)
        long_term_sma_dataframe = long_term_sma_dataframe.tail(sma_moving_average_lookback_time_period)

        sma_cross_df1 = pd.merge(short_term_sma_dataframe, long_term_sma_dataframe, left_index=True, right_index=True)

        sma_cross_up_ticker_name_list = []
        sma_cross_down_ticker_name_list = []

        for ticker in self.sp_500_symbols_list:
            sma_cross_df2 = sma_cross_df1.filter(regex=rf"^{ticker}_")

            #Detect moving average cross up event or cross down event
                #https://stackoverflow.com/questions/28345261/python-and-pandas-moving-average-crossover
            #Shift the column values down one row. The last value is removed and the top column becomes NaN.
            previous_short_term_moving_average_df1 = sma_cross_df2[f'{ticker}_{short_term_moving_average}_sma'].shift(1)

            previous_long_term_moving_average_df1 = sma_cross_df2[f'{ticker}_{long_term_moving_average}_sma'].shift(1)

            short_term_sma_cross_up_df1 = ((sma_cross_df2[f'{ticker}_{short_term_moving_average}_sma'] > sma_cross_df2[f'{ticker}_{long_term_moving_average}_sma']) & (previous_short_term_moving_average_df1 <= previous_long_term_moving_average_df1))

            #Notice the greater than and lesser than symbols are reversed for the cross down dataframe
            short_term_sma_cross_down_df1 = ((sma_cross_df2[f'{ticker}_{short_term_moving_average}_sma'] < sma_cross_df2[f'{ticker}_{long_term_moving_average}_sma']) & (previous_short_term_moving_average_df1 >= previous_long_term_moving_average_df1))

            #Count the number of cross up events by counting the number of True values in the boolean array
            number_of_cross_up_events = np.count_nonzero(short_term_sma_cross_up_df1)
            number_of_cross_down_events = np.count_nonzero(short_term_sma_cross_down_df1)

            #If there is 1 or more True values (i.e., cross up events), then append the name of the ticker to sma_cross_up_ticker_name_list
            if number_of_cross_up_events >= 1:
                sma_cross_up_ticker_name_list.append(ticker)
            #Else if (elif) there is 1 or more True values (i.e., cross down events), then append the name of the ticker to sma_cross_down_ticker_name_list
            elif number_of_cross_down_events >= 1:
                sma_cross_down_ticker_name_list.append(ticker)
            else:
                pass

        print('Analyzing Simple Moving Average Strategy...DONE')

        return sma_cross_up_ticker_name_list, sma_cross_down_ticker_name_list


def main():

    ##Uncomment the next two lines if you want to see the entire DataFrame
    #pd.set_option('display.max_columns', 999)
    #pd.set_option('display.max_rows', 5000)

    #How much data to pull and in what intervals
    #Ticker.history() parameters
        #aapl.history(period='max')
        #aapl.history(start='2019-05-01') #Default end date is now
        #aapl.history(end='2018-12-31') #Default start date is 1900-01-01
        #Period options = 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
        #Interval options = 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
    data_history_period = '5y'
    data_history_period_interval = '1d'

    short_term_sma_period = 50
    long_term_sma_period = 200
    sma_moving_average_lookback_time_period = 5

    generic_trading_algorithm = Generic_Trading_Algorithm()

    open_df1, high_df1, low_df1, close_df1, adjusted_close_df1, volume_close_df1, dividend_df1 = generic_trading_algorithm.get_stock_price_data_yahooquery(data_history_period=data_history_period, data_history_period_interval=data_history_period_interval)

    fifty_sma_df1 = generic_trading_algorithm.calc_sma(close_price_dataframe=close_df1, period=short_term_sma_period)

    two_hundred_sma_df1 = generic_trading_algorithm.calc_sma(close_price_dataframe=close_df1, period=long_term_sma_period)

    #TA-Lib matype parameter numbers list
        #TA-Lib uses numbers which correspond to different types of moving averages you can use for a particular technical analysis indicator
        #List of values for the Moving Average Type:
            #https://www.quantopian.com/posts/macd-exponential-or-weighted
            #0: SMA (simple)
            #1: EMA (exponential)
            #2: WMA (weighted)
            #3: DEMA (double exponential)
            #4: TEMA (triple exponential)
            #5: TRIMA (triangular)
            #6: KAMA (Kaufman adaptive)
            #7: MAMA (Mesa adaptive)
            #8: T3 (triple exponential T3)
    upper_twenty_bollinger_bands, middle_twenty_bollinger_bands, lower_twenty_bollinger_bands = generic_trading_algorithm.calc_bollinger_bands(
                                                    close_price_dataframe=close_df1, 
                                                    timeperiod=20, 
                                                    nbdevup=2, 
                                                    nbdevdn=2, 
                                                    matype=3
                                                    )

    #Strategy simple moving average
    sma_cross_up_ticker_name_list, sma_cross_down_ticker_name_list = generic_trading_algorithm.strategy_sma_crossover(
                                                short_term_sma_dataframe=fifty_sma_df1, 
                                                long_term_sma_dataframe=two_hundred_sma_df1, 
                                                short_term_moving_average=short_term_sma_period, 
                                                long_term_moving_average=long_term_sma_period, 
                                                sma_moving_average_lookback_time_period=sma_moving_average_lookback_time_period
                                                )

    print(f"These are the {len(sma_cross_up_ticker_name_list)} stocks in which the {short_term_sma_period} simple moving average crossed ABOVE the {long_term_sma_period} simple moving average in the past {sma_moving_average_lookback_time_period} days:\n{sma_cross_up_ticker_name_list}\n\n")
    #On 7/16/2020 these were the stocks which met the simple moving average cross up criteria...
    #These are the 13 stocks in which the 50 simple moving average crossed ABOVE the 200 simple moving average in the past 5 days:
    #['BLL', 'CPRT', 'CTAS', 'EMN', 'EQ', 'FCX', 'GWW', 'IQV', 'JNPR', 'LIFE', 'PCAR', 'PDCO', 'TWTR']

    print(f"These are the {len(sma_cross_down_ticker_name_list)} stocks in which the {short_term_sma_period} simple moving average crossed BELOW the {long_term_sma_period} simple moving average in the past {sma_moving_average_lookback_time_period} days:\n{sma_cross_down_ticker_name_list}")
    #On 7/16/2020 these were the stocks which met the simple moving average cross down criteria...
    #These are the 1 stocks in which the 50 simple moving average crossed BELOW the 200 simple moving #average in the past 5 days:
    #['PCG']

    end_time = timer()
    total_time = end_time - start_time
    minutes, seconds = divmod(total_time, 60)
    hours, minutes = divmod(minutes, 60)
    print("\n\nTotal Run Time: %d:%02d:%02d" % (hours, minutes, seconds))


if __name__ == "__main__":

    main()
