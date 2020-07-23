#Lesson #8: Generic Trading Algorithm With XLWings Integration

#This algorithm is the same as Generic_Trading_Algorithm.py except I only get stock data. I don't calculate the technical indicators.


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
import xlwings as xw
import os
import sys
import path
import datetime


class Generic_Trading_Algorithm():

    def __init__(self, reference_table_data_dataframe: pd.DataFrame):

        self.python_script_file_path = os.path.dirname(sys.argv[0])

        self.data_folder_path = self.python_script_file_path + "\\Data\\"

        self.stock_data_workbook_excel_file_path = self.python_script_file_path + "\\Data\\Stock_Data_Workbook.xlsx"

        self.reference_table_data_dataframe = reference_table_data_dataframe

###################################################################################################################################
        self.yahoo_query_username = 'YAHOO_EMAIL_ADDRESS'
        self.yahoo_query_password = 'YAHOO_EMAIL_ADDRESS_PASSWORD'
###################################################################################################################################

        #For simplicity's sake we will just pull data for the 5 stocks in our test symbols list

        #Fetch symbols list of all stocks in the S&P 500
        #sp_500_url = "http://www.kibot.com/Files/2/SP_500_Intraday.txt"
        #sp_500_csv_df1 = pd.read_csv(sp_500_url, delimiter='\t', header=4, engine='python', usecols=['#','Symbol'])
        #sp_500_table_range = sp_500_csv_df1.loc[sp_500_csv_df1['#']=='Delisted:'].index.tolist()
        #sp_500_csv_df1 = sp_500_csv_df1.iloc[:sp_500_table_range[0]+1]
        #sp_500_csv_df1 = sp_500_csv_df1.drop(sp_500_csv_df1.tail(1).index)
        #sp_500_raw_symbols_list = sp_500_csv_df1.iloc[:, 1].tolist()

        #Replace the period in certain stock symbols like BF.B and BRK.B to BF-B and BRK-B because Yahoo Finance uses dashes instead of periods
            #See Error Debugging Example.docx for details
        #Set will remove duplicates
        #List converts the set back into a list dtype
        #Sorted will put the list in alphabetical order
        #self.sp_500_symbols_list = sorted(list(set([x.replace(".", "-") for x in sp_500_raw_symbols_list])))

        #Test symbols list
        self.sp_500_symbols_list = ['AAPL', 'BMY', 'CSCO', 'FB', 'NVDA']


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


    #Export the closing price dataframes to a single Excel workbook, but create a new sheet each time
    def export_to_excel_one_workbook_multiple_spreadsheets(self, close_price_dataframe: pd.DataFrame):

        print('Exporting to Excel spreadsheet...')

        wb = xw.Book(self.stock_data_workbook_excel_file_path)

        now = datetime.datetime.now()

        xw.main.sheets.add(name=(now.strftime("%Y-%m-%d %H""h""%M""m""%S""s Report")), after='Instructions')

        self.active_sheet_name = xw.sheets.active

        #Format the new Excel worksheet
        #Cell alignment
            #http://docs.xlwings.org/en/stable/missing_features.html
            #http://stackoverflow.com/questions/8490265/pywin32-excel-formatting
            #http://stackoverflow.com/questions/6952084/excel-cell-alignments-numerical-values-for-e-g-xlleft-xlright-or-xlcenter
                #VerticalAlignment:
                    #Top: -4160
                    #Center: -4108
                    #Bottom: -4107
                #HorizontalAlignment:
                    #Left: -4131
                    #Center: -4108
                    #Right: -4152
        self.active_sheet_name.range('$A$1:$XFD$1048576').api.VerticalAlignment = -4160
        self.active_sheet_name.range('$A$1:$XFD$1048576').api.HorizontalAlignment = -4131

        #Font name
            #xlwings Cheat Sheet
            #http://nbviewer.jupyter.org/github/pybokeh/jupyter_notebooks/blob/master/xlwings/Excel_Formatting.ipynb
        self.active_sheet_name.range('$A$1:$XFD$1048576').api.Font.Name = "Calibri"
        self.active_sheet_name.range('$A$1:$XFD$1048576').api.Font.Size = 11

        #Set active sheet zoom to 75%
        excel = xw.apps.active
        excel.api.ActiveWindow.Zoom = 75

        #Export close price dataframe to Excel spreadsheet
        self.active_sheet_name.range('A1').options(index=True, header=True).value = close_price_dataframe

        #Total number of columns in Excel
        #Add 1 to account for the index
        total_number_of_excel_columns = (len((close_price_dataframe.columns)))+1

        #Total number of rows in Excel
        #Add 1 to account for the column headers
        total_number_of_excel_rows = (len((close_price_dataframe)))+1

        #Row 1 Formatting
        #(row, column)
        self.active_sheet_name.range((1, 1), (1, total_number_of_excel_columns)).api.Font.Bold = True
        self.active_sheet_name.range((1, 1), (1, total_number_of_excel_columns)).api.HorizontalAlignment = -4108

        #Freeze top row
        wb.api.Windows(1).SplitColumn = 0
        wb.api.Windows(1).SplitRow = 1
        wb.api.Windows(1).FreezePanes = True

        #Add Autofilter
            #You can add a filter if you would like using the following line. This is the same thing as going to Sort & Filter --> Filter.
            #Since we are going to insert a table, inserting a filter is unnecessary
            #https://stackoverflow.com/questions/2967949/setting-criteria-on-an-autofilter-in-pywin32
            #https://docs.microsoft.com/en-us/office/vba/api/excel.range.autofilter
        #self.active_sheet_name.range((1, 1), (1, total_number_of_excel_columns)).api.AutoFilter()

###################################################################################################################################

        #CLOSE PRICE DATAFRAME SECTION

        #Get Excel column numbers so that you can reference where the column will be when you want to apply formatting
            #Adding 2 because the first column in a pandas dataframe is 0 and we are including the dataframe's index in the export to Excel
        #If pulling all the S&P 500 stocks, you will get the tickers as the column headers
        try:
            fb_excel_column_number = close_price_dataframe.columns.get_loc('FB') + 2
            nvda_excel_column_number = close_price_dataframe.columns.get_loc('NVDA') + 2
        #When using the test list, the column headers have _close after the stock symbol (e.g., FB_close)
        except:
            fb_excel_column_number = close_price_dataframe.columns.get_loc('FB_close') + 2
            nvda_excel_column_number = close_price_dataframe.columns.get_loc('NVDA_close') + 2

        #Insert table into Excel using xlwings
            #Creating and naming a table in xlwings
                #https://stackoverflow.com/questions/57478995/creating-and-naming-a-table-in-xlwings
            #Format Table in xlwings
                #https://stackoverflow.com/questions/50624336/format-table-in-xlwings
        #close_price_data_table_range = self.active_sheet_name.range('A1').expand('table')
        #TableStyleMedium2 is the default table with alternating blue and white rows
        #self.active_sheet_name.api.ListObjects.Add(1, self.active_sheet_name.api.Range(close_price_data_table_range.address)).TableStyle = 'TableStyleMedium2'
        #TableStyleMedium7 is a table with alternating green and white rows
        #self.active_sheet_name.api.ListObjects.Add(1, self.active_sheet_name.api.Range(close_price_data_table_range.address)).TableStyle = 'TableStyleMedium7'
        close_price_data_table_range = self.active_sheet_name.range((1, 1), (total_number_of_excel_rows, total_number_of_excel_columns))
        self.active_sheet_name.api.ListObjects.Add(1, self.active_sheet_name.api.Range(close_price_data_table_range.address)).TableStyle = 'TableStyleMedium2'

        #Fill cell backgrounds
            #Only will fill FB column
        self.active_sheet_name.range((1, fb_excel_column_number), (total_number_of_excel_rows, fb_excel_column_number)).color = (255, 255, 0)

        #Font color
            #NVDA column font will be red
        self.active_sheet_name.range((1, nvda_excel_column_number), (total_number_of_excel_rows, nvda_excel_column_number)).api.Font.Color = xw.utils.rgb_to_int((255, 0, 0))

        #Number formatting for the entire close price dataframe
        #Set the index column to be formatted like a date (the index should already be in yyyy-mm-dd format in the dataframe, but I just decided to include as another example)
        self.active_sheet_name.range((1, 1), (total_number_of_excel_rows, 1)).api.NumberFormat = 'yyyy-mm-dd'
        self.active_sheet_name.range((1, 2), (total_number_of_excel_rows, total_number_of_excel_columns)).api.NumberFormat = '$#,##0.00'

###################################################################################################################################

        #REFERENCE TABLE DIRECTLY BELOW THE CLOSE PRICE DATAFRAME SECTION

        #Export reference table dataframe to Excel spreadsheet
        self.active_sheet_name.range((total_number_of_excel_rows+3, 1)).options(index=False, header=True).value = self.reference_table_data_dataframe

        #Reference table directly below the closing price dataframe
        higher_reference_table_bottom_row_number = total_number_of_excel_rows + 3 + len(self.reference_table_data_dataframe)
        self.active_sheet_name.range((higher_reference_table_bottom_row_number+4, 1)).options(index=False, header=True).value = self.reference_table_data_dataframe

        #Add comment to cell with xlwings
            #https://stackoverflow.com/questions/37123153/using-python-xlwings-module-to-create-cell-comments
        #Format Excel comments using xlwings and how to bold only part of a string in an Excel cell
            #https://stackoverflow.com/questions/45754774/using-pywin32-xlwings-how-do-you-read-the-text-of-an-existing-comment
            #https://stackoverflow.com/questions/47222373/add-comment-to-excel-using-python-win32
            #If trying to overwrite a comment, you need to clear it first
            #How Do I Bold only part of a string in an excel cell with python
                #https://stackoverflow.com/questions/26489355/how-do-i-bold-only-part-of-a-string-in-an-excel-cell-with-python/26490194#26490194
        cmt1_message = "Ryan Young:\nThis is the reference table directly below the close price dataframe."

        #Adding the comment to the first column header
        cmt1 = self.active_sheet_name.range((total_number_of_excel_rows+3, 1)).api.AddComment(Text=cmt1_message)
        #cmt1.Shape.TextFrame.Characters().Font.Bold = False
        #Make Opollo look like the author of the comment
            #How Do I Bold only part of a string in an excel cell with python
                #https://stackoverflow.com/questions/26489355/how-do-i-bold-only-part-of-a-string-in-an-excel-cell-with-python/26490194#26490194
        #The following line works when you test this on its own in the Python interpreter. However, it throws a pywin error when you execute the code in Visual Studio's debugger. It might work on other systems though.
        #cmt1.Shape.TextFrame.Characters(1, 12).api.Font.Bold = True
        #Unbold all the characters after "From Opollo:"
        cmt1.Shape.TextFrame.Characters(12, ).Font.Bold = False
        cmt1.Shape.TextFrame.Characters().Font.Name = 'Calibri'
        cmt1.Shape.TextFrame.Characters().Font.Size = 11

        #Size the comment box. You can either have Excel autosize the comment box or you can manually set the dimensions.
            #I decided to just use auto size
        self.active_sheet_name.range((total_number_of_excel_rows+3, 1)).api.Comment.Shape.TextFrame.AutoSize = True
        #cmt1.Shape.Height = 450
        #cmt1.Shape.Width = 900

###################################################################################################################################

        #LOWEST REFERENCE TABLE IN COLUMN A SECTION
            #Has cell borders and looks like an Excel table. In other words, it looks like you highlighted all the cells and went to Insert --> Table in Excel. But, it's actually not an Excel table. We just applied a lot of formatting to make it look like one.

        #Draw borders around cells in the reference table directly below the closing price dataframe
            #https://stackoverflow.com/questions/37866812/set-border-using-python-xlwings
        higher_reference_table_bottom_table_cell_border_range = self.active_sheet_name.range((higher_reference_table_bottom_row_number+4, 1), (higher_reference_table_bottom_row_number+4+len(self.reference_table_data_dataframe), len(self.reference_table_data_dataframe.columns)))
        #The following line is generating the numbers associated with the types of borders (i.e., it is generating the border IDs)
            #The border ID numbers are 7 through 13
        for border_id in xw.xrange(7, 13):
            higher_reference_table_bottom_table_cell_border_range.api.Borders(border_id).LineStyle = 1
            higher_reference_table_bottom_table_cell_border_range.api.Borders(border_id).Weight = 2
            #Change cell border color
            higher_reference_table_bottom_table_cell_border_range.api.Borders(border_id).Color = xw.utils.rgb_to_int((155, 194, 230))

        #Change background color of the column headers in the table at the very bottom
            #(91, 155, 213) is for the RGB color format [i.e., RGB(91, 155, 213)]
        self.active_sheet_name.range((higher_reference_table_bottom_row_number+4, 1), (higher_reference_table_bottom_row_number+4, len(self.reference_table_data_dataframe.columns))).color = (91, 155, 213)

        #Make the column headers font white in the table at the very bottom
        self.active_sheet_name.range((higher_reference_table_bottom_row_number+4, 1), (higher_reference_table_bottom_row_number+4, len(self.reference_table_data_dataframe.columns))).api.Font.Color = xw.utils.rgb_to_int((255, 255, 255))

        #Bold the column headers font in the table at the very bottom
        self.active_sheet_name.range((higher_reference_table_bottom_row_number+4, 1), (higher_reference_table_bottom_row_number+4, len(self.reference_table_data_dataframe.columns))).api.Font.Bold = True

        #Center the column headers font in the table at the very bottom
        self.active_sheet_name.range((higher_reference_table_bottom_row_number+4, 1), (higher_reference_table_bottom_row_number+4, len(self.reference_table_data_dataframe.columns))).api.HorizontalAlignment = -4108

        #Alternate the background color of the rows in the table at the very bottom
        #Note that step=2 in the following line. This will make the counter increase by 2 after each iteration.
        for row in range(higher_reference_table_bottom_row_number+4+1, higher_reference_table_bottom_row_number+4+1+len(self.reference_table_data_dataframe)+1, 2):
            #You need to fill each column though so just use the default step=1 (you can also just not include it)
            for column in range(1, len(self.reference_table_data_dataframe.columns)+1):
                self.active_sheet_name.range((row, 1), (row, column)).color = (221, 235, 247)

###################################################################################################################################

        #REFERENCE TABLE TO THE BOTTOM RIGHT OF THE CLOSE PRICE DATAFRAME SECTION

        #Reference table to the right of the close price dataframe
            #Has bold column headers
        right_reference_table_bottom_column_number = total_number_of_excel_columns + 4

        self.active_sheet_name.range((higher_reference_table_bottom_row_number+4, right_reference_table_bottom_column_number)).options(index=False, header=True).value = self.reference_table_data_dataframe

        #Bold the column headers
        self.active_sheet_name.range((higher_reference_table_bottom_row_number+4, right_reference_table_bottom_column_number), (higher_reference_table_bottom_row_number+4, right_reference_table_bottom_column_number+len(self.reference_table_data_dataframe.columns))).api.Font.Bold = True

###################################################################################################################################

        #Other helpful examples
        #Merge cells
        #Just adding some dummy text
        self.active_sheet_name.range((1, total_number_of_excel_columns+4)).value = "Ryan Young"
        self.active_sheet_name.range((1, total_number_of_excel_columns+4), (1, total_number_of_excel_columns+5)).api.MergeCells = True
        self.active_sheet_name.range((1, total_number_of_excel_columns+4), (1, total_number_of_excel_columns+5)).api.Font.Bold = True
        self.active_sheet_name.range((1, total_number_of_excel_columns+4), (1, total_number_of_excel_columns+5)).api.HorizontalAlignment = -4108

        #Basically, we are going to insert a formula into Excel using relative positioning
            #Get Excel calculations dynamically
                #https://stackoverflow.com/questions/45867882/python-xlwings-copy-paste-formula-with-relative-cell-references/52080566
        #Just adding some dummy data
        number_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]
        #The list will appear vertically (i.e., down the rows) because I set transpose=True
        self.active_sheet_name.range((2, total_number_of_excel_columns+4)).options(transpose=True).value = number_list
        #The list will appear horizontally (i.e., across the columns) because I set transpose=False
        #self.active_sheet_name.range((2, total_number_of_excel_columns+4)).options(transpose=False).value = number_list

        self.active_sheet_name.range((9, total_number_of_excel_columns+6)).value = "Sum Formula Cell"
        #R[-18]C[-2] --> means find the value which is 18 rows above and 2 columns to the left from the cell where the forluma is being calculated
        self.active_sheet_name.range((10, total_number_of_excel_columns+6)).api.FormulaR1C1 = '=(R[-18]C[-2] + R[-16]C[-2] + R[-14]C[-2] + R[-12]C[-2] + R[-10]C[-2] + R[-8]C[-2] + R[-6]C[-2] + R[-4]C[-2] + R[-2]C[-2])'

        #Another example from some old code I wrote. Note the use of the for loop.
        #for i in range(9, 9+len(self.sp_500_symbols_list)):
        #    xw.Range((48, 9), (48, i)).api.FormulaR1C1 = '=(R[-18]C + R[-16]C + R[-14]C + R[-12]C + R[-10]C + R[-8]C + R[-6]C + R[-4]C + R[-2]C)'
        #    xw.Range((61, 9), (61, i)).api.FormulaR1C1 = '=(R[-8]C + R[-6]C + R[-4]C + R[-2]C)'

        #Finish the sheet formatting. I generally set column widths last.

        #Column widths
        #Autofit all columns then set certain column widths
            #You have to let it know which cell to autofit according to
                #In this case, it will autofit based on the text in the first row
        self.active_sheet_name.range((1, 1), (1, total_number_of_excel_columns)).autofit()

        #Manually set column widths
            #Obviously you should manually set widths AFTER autofitting the other columns
            #In this case we will make the NVDA column really wide
        self.active_sheet_name.range((1, nvda_excel_column_number)).column_width = 25

        #Cursor select cell
            #Have the cursor select a particular cell
            #This is useful if you have a lot of columns and the most important columns are towards the end
        self.active_sheet_name.range((1, total_number_of_excel_columns+4)).select()

        print('Exporting to Excel spreadsheet...DONE')


    #Create a new workbook (i.e., new Excel file) each time behind scenes and save the workbook
        #For this example, I don't include all the formatting so hopefully it's easier for you to see the difference between export_to_excel_one_workbook_multiple_spreadsheets() and export_to_excel_multiple_workbooks()
    def export_to_excel_multiple_workbooks(self, close_price_dataframe: pd.DataFrame):

        print('Exporting to Excel workbook...')

        #Create new Excel workbook
        excel_app = xw.App(visible=False)
        wb = xw.books.add()

        #Set active sheet as instance variable
        self.active_sheet_name = xw.sheets.active

        #Format the new Excel worksheet
        #Cell alignment
            #http://docs.xlwings.org/en/stable/missing_features.html
            #http://stackoverflow.com/questions/8490265/pywin32-excel-formatting
            #http://stackoverflow.com/questions/6952084/excel-cell-alignments-numerical-values-for-e-g-xlleft-xlright-or-xlcenter
                #VerticalAlignment:
                    #Top: -4160
                    #Center: -4108
                    #Bottom: -4107
                #HorizontalAlignment:
                    #Left: -4131
                    #Center: -4108
                    #Right: -4152
        self.active_sheet_name.range('$A$1:$XFD$1048576').api.VerticalAlignment = -4160
        self.active_sheet_name.range('$A$1:$XFD$1048576').api.HorizontalAlignment = -4131

        #Font name
            #xlwings Cheat Sheet
            #http://nbviewer.jupyter.org/github/pybokeh/jupyter_notebooks/blob/master/xlwings/Excel_Formatting.ipynb
        self.active_sheet_name.range('$A$1:$XFD$1048576').api.Font.Name = "Calibri"
        self.active_sheet_name.range('$A$1:$XFD$1048576').api.Font.Size = 11

        #Set active sheet zoom to 75%
        excel_app.api.ActiveWindow.Zoom = 75

        #Export close price dataframe to Excel spreadsheet
        self.active_sheet_name.range('A1').options(index=True, header=True).value = close_price_dataframe

        #Total number of columns in Excel
        #Add 1 to account for the index
        total_number_of_excel_columns = (len((close_price_dataframe.columns)))+1

        #Total number of rows in Excel
        #Add 1 to account for the column headers
        total_number_of_excel_rows = (len((close_price_dataframe)))+1

        #Row 1 Formatting
        #(row, column)
        self.active_sheet_name.range((1, 1), (1, total_number_of_excel_columns)).api.Font.Bold = True
        self.active_sheet_name.range((1, 1), (1, total_number_of_excel_columns)).api.HorizontalAlignment = -4108

        #Freeze top row
        wb.api.Windows(1).SplitColumn = 0
        wb.api.Windows(1).SplitRow = 1
        wb.api.Windows(1).FreezePanes = True

        #Number formatting for the entire close price dataframe
        #Set the index column to be formatted like a date (the index should already be in yyyy-mm-dd format in the dataframe, but I just decided to include as another example)
        self.active_sheet_name.range((1, 1), (total_number_of_excel_rows, 1)).api.NumberFormat = 'yyyy-mm-dd'
        self.active_sheet_name.range((1, 2), (total_number_of_excel_rows, total_number_of_excel_columns)).api.NumberFormat = '$#,##0.00'

        #Column widths
        #Autofit all columns then set certain column widths
            #You have to let it know which cell to autofit according to
                #In this case, it will autofit based on the text in the first row
        self.active_sheet_name.range((1, 1), (1, total_number_of_excel_columns)).autofit()

        #Autofit the Date column based on the second row cell's width
        self.active_sheet_name.range((2, 1)).autofit()

        #Save Excel workbook
        now = datetime.datetime.now()
        workbook_name_date = now.strftime("%Y_%m_%d %H""%M")
        wb.save(f"{self.data_folder_path}{workbook_name_date} Report")

        #Close Excel workbook
        wb.close()

        #Quit Excel instance
        excel_app.quit()

        print('Exporting to Excel workbook...DONE')


def main():

    ##Uncomment the next two lines if you want to see the entire DataFrame
    #pd.set_option('display.max_columns', 999)
    #pd.set_option('display.max_rows', 5000)

    #Reference table
    reference_table_data = {
                            'county': ['Cochice', 'Pima', 'Santa Cruz', 'Maricopa', 'Yuma'], 
                            'year': [2012, 2012, 2013, 2014, 2014], 
                            'reports': [4, 24, 31, 2, 3]
                            }
    reference_table_data_df1 = pd.DataFrame(reference_table_data)

    #How much data to pull and in what intervals
    #Ticker.history() parameters
        #aapl.history(period='max')
        #aapl.history(start='2019-05-01') #Default end date is now
        #aapl.history(end='2018-12-31') #Default start date is 1900-01-01
        #Period options = 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
        #Interval options = 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo

    #Pulling 5 years of data is a little excessive for this exercise so I will just pull 1 month of data
    #data_history_period = '5y'
    data_history_period = '1mo'
    data_history_period_interval = '1d'

    short_term_sma_period = 50
    long_term_sma_period = 200
    sma_moving_average_lookback_time_period = 5

    generic_trading_algorithm = Generic_Trading_Algorithm(reference_table_data_dataframe=reference_table_data_df1)

    open_df1, high_df1, low_df1, close_df1, adjusted_close_df1, volume_close_df1, dividend_df1 = generic_trading_algorithm.get_stock_price_data_yahooquery(data_history_period=data_history_period, data_history_period_interval=data_history_period_interval)

    #I commented out the technical indicator functions because we only need to export the closing price data for this particular exercise

    #fifty_sma_df1 = generic_trading_algorithm.calc_sma(close_price_dataframe=close_df1, period=short_term_sma_period)

    #two_hundred_sma_df1 = generic_trading_algorithm.calc_sma(close_price_dataframe=close_df1, period=long_term_sma_period)

    ##TA-Lib matype parameter numbers list
    #    #TA-Lib uses numbers which correspond to different types of moving averages you can use for a particular technical analysis indicator
    #    #List of values for the Moving Average Type:
    #        #https://www.quantopian.com/posts/macd-exponential-or-weighted
    #        #0: SMA (simple)
    #        #1: EMA (exponential)
    #        #2: WMA (weighted)
    #        #3: DEMA (double exponential)
    #        #4: TEMA (triple exponential)
    #        #5: TRIMA (triangular)
    #        #6: KAMA (Kaufman adaptive)
    #        #7: MAMA (Mesa adaptive)
    #        #8: T3 (triple exponential T3)
    #upper_twenty_bollinger_bands, middle_twenty_bollinger_bands, lower_twenty_bollinger_bands = generic_trading_algorithm.calc_bollinger_bands(
    #                                                close_price_dataframe=close_df1, 
    #                                                timeperiod=20, 
    #                                                nbdevup=2, 
    #                                                nbdevdn=2, 
    #                                                matype=3
    #                                                )

    ##Strategy simple moving average
    #sma_cross_up_ticker_name_list, sma_cross_down_ticker_name_list = generic_trading_algorithm.strategy_sma_crossover(
    #                                            short_term_sma_dataframe=fifty_sma_df1, 
    #                                            long_term_sma_dataframe=two_hundred_sma_df1, 
    #                                            short_term_moving_average=short_term_sma_period, 
    #                                            long_term_moving_average=long_term_sma_period, 
    #                                            sma_moving_average_lookback_time_period=sma_moving_average_lookback_time_period
    #                                            )

    #print(f"These are the {len(sma_cross_up_ticker_name_list)} stocks in which the {short_term_sma_period} simple moving average crossed ABOVE the {long_term_sma_period} simple moving average in the past {sma_moving_average_lookback_time_period} days:\n{sma_cross_up_ticker_name_list}\n\n")
    ##On 7/16/2020 these were the stocks which met the simple moving average cross up criteria...
    ##These are the 13 stocks in which the 50 simple moving average crossed ABOVE the 200 simple moving average in the past 5 days:
    ##['BLL', 'CPRT', 'CTAS', 'EMN', 'EQ', 'FCX', 'GWW', 'IQV', 'JNPR', 'LIFE', 'PCAR', 'PDCO', 'TWTR']

    #print(f"These are the {len(sma_cross_down_ticker_name_list)} stocks in which the {short_term_sma_period} simple moving average crossed BELOW the {long_term_sma_period} simple moving average in the past {sma_moving_average_lookback_time_period} days:\n{sma_cross_down_ticker_name_list}")
    ##On 7/16/2020 these were the stocks which met the simple moving average cross down criteria...
    ##These are the 1 stocks in which the 50 simple moving average crossed BELOW the 200 simple moving #average in the past 5 days:
    ##['PCG']

    #Export the closing price dataframes to a single Excel workbook, but create a new sheet each time
    generic_trading_algorithm.export_to_excel_one_workbook_multiple_spreadsheets(close_price_dataframe=close_df1)

    #Create a new workbook (i.e., new Excel file) each time behind scenes and save the workbook
        #For this example, I don't include all the formatting so hopefully it's easier for you to see the difference between export_to_excel_one_workbook_multiple_spreadsheets() and export_to_excel_multiple_workbooks()
    generic_trading_algorithm.export_to_excel_multiple_workbooks(close_price_dataframe=close_df1)

    end_time = timer()
    total_time = end_time - start_time
    minutes, seconds = divmod(total_time, 60)
    hours, minutes = divmod(minutes, 60)
    print("\n\nTotal Run Time: %d:%02d:%02d" % (hours, minutes, seconds))


if __name__ == "__main__":

    main()
