#Lesson #4 Yahooquery Get Financial Statement Data
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

#symbols_list = ['AAPL']
#symbols_list = ['AAPL', 'BMY']
symbols_list = ['AAPL', 'BMY', 'CRON', 'CSCO', 'FB', 'MLM', 'MSFT', 'NVDA', 'TNK', 'XOM']

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
tickers = Ticker(symbols_list, asynchronous=False, max_workers=8, username='YAHOO_EMAIL_ADDRESS', password='YAHOO_EMAIL_ADDRESS_PASSWORD')

#Financial statement data
#tickers.company_officers()
#tickers.earning_history()
#tickers.earnings_trend()
#tickers.esg_scores()
#tickers.financial_data()
#tickers.fund_ownership()
#tickers.grading_history()
#tickers.key_stats()
#tickers.insider_holders()
#tickers.insider_transactions()
#tickers.institution_ownership()
#tickers.major_holders()
#tickers.news()
#tickers.recommendation_trend()
#tickers.sec_filings()
#tickers.share_purchase_activity()
#tickers.technical_insights()

##The following methods take a frequency argument.  If nothing is provided, annual data will be returned.  To return quarterly data, pass "q" as an argument.
#tickers.balance_sheet()  # Defaults to Annual
#tickers.balance_sheet(frequency="q")
#df1 = tickers.cash_flow(frequency="q")
#print(df1)
#df1.columns

#modules = ['cashflowStatementHistoryQuarterly', 'cashflowStatementHistory', 'balanceSheetHistory', 'balanceSheetHistoryQuarterly', 'incomeStatementHistory', 'incomeStatementHistoryQuarterly']

#tickers.income_statement(frequency="q")

#See list of allowable modules
#aapl = Ticker('aapl')
#All modules will get data for all the modules
#aapl.all_modules

#You can get multiple modules in the same call
    #https://github.com/dpguthrie/yahooquery/blob/master/README.md#accessing-multiple-modules
modules = ['cashflowStatementHistory', 
        'cashflowStatementHistoryQuarterly', 
        'balanceSheetHistory', 
        'balanceSheetHistoryQuarterly', 
        'incomeStatementHistory', 
        'incomeStatementHistoryQuarterly']

financial_statement_data = tickers.get_modules(modules)

cash_flow_annual_list = []
balance_sheet_annual_list = []
income_statement_annual_list = []
cash_flow_quarterly_list = []
balance_sheet_quarterly_list = []
income_statement_quarterly_list = []

cash_flow_annual_column_name_list = []
balance_sheet_annual_column_name_list = []
income_statement_annual_column_name_list = []
cash_flow_quarterly_column_name_list = []
balance_sheet_quarterly_column_name_list = []
income_statement_quarterly_column_name_list = []

for ticker in symbols_list:
    cash_flow_annual_df1 = pd.DataFrame(financial_statement_data[ticker]['cashflowStatementHistory']['cashflowStatements'])
    cash_flow_annual_df2 = cash_flow_annual_df1.add_prefix(f"{ticker}_")
    cash_flow_annual_column_name_list.append(cash_flow_annual_df2.columns.values.tolist())
    cash_flow_annual_list.append(cash_flow_annual_df2)

    balance_sheet_annual_df1 = pd.DataFrame(financial_statement_data[ticker]['balanceSheetHistory']['balanceSheetStatements'])
    balance_sheet_annual_df2 = balance_sheet_annual_df1.add_prefix(f"{ticker}_")
    balance_sheet_annual_column_name_list.append(balance_sheet_annual_df2.columns.values.tolist())
    balance_sheet_annual_list.append(balance_sheet_annual_df2)

    income_statement_annual_df1 = pd.DataFrame(financial_statement_data[ticker]['incomeStatementHistory']['incomeStatementHistory'])
    income_statement_annual_df2 = income_statement_annual_df1.add_prefix(f"{ticker}_")
    income_statement_annual_column_name_list.append(income_statement_annual_df2.columns.values.tolist())
    income_statement_annual_list.append(income_statement_annual_df2)

    cash_flow_quarterly_df1 = pd.DataFrame(financial_statement_data[ticker]['cashflowStatementHistoryQuarterly']['cashflowStatements'])
    cash_flow_quarterly_df2 = cash_flow_quarterly_df1.add_prefix(f"{ticker}_")
    cash_flow_quarterly_column_name_list.append(cash_flow_quarterly_df2.columns.values.tolist())
    cash_flow_quarterly_list.append(cash_flow_quarterly_df2)

    balance_sheet_quarterly_df1 = pd.DataFrame(financial_statement_data[ticker]['balanceSheetHistoryQuarterly']['cashflowStatements'])
    balance_sheet_quarterly_df2 = balance_sheet_quarterly_df1.add_prefix(f"{ticker}_")
    balance_sheet_quarterly_column_name_list.append(balance_sheet_quarterly_df2.columns.values.tolist())
    balance_sheet_quarterly_list.append(balance_sheet_quarterly_df2)

    income_statement_quarterly_df1 = pd.DataFrame(financial_statement_data[ticker]['incomeStatementHistoryQuarterly']['cashflowStatements'])
    income_statement_quarterly_df2 = cash_flow_quarterly_df1.add_prefix(f"{ticker}_")
    income_statement_quarterly_column_name_list.append(income_statement_quarterly_df2.columns.values.tolist())
    income_statement_quarterly_list.append(income_statement_quarterly_df2)

#Flatten column name lists
    #https://stackoverflow.com/questions/952914/how-to-make-a-flat-list-out-of-list-of-lists
cash_flow_annual_column_name_flattened_list = [x for sublist in cash_flow_annual_column_name_list for x in sublist]
balance_sheet_annual_column_name_flattened_list = [x for sublist in balance_sheet_annual_column_name_list for x in sublist]
income_statement_annual_column_name_flattened_list = [x for sublist in income_statement_annual_column_name_list for x in sublist]
cash_flow_quarterly_column_name_flattened_list = [x for sublist in cash_flow_quarterly_column_name_list for x in sublist]
balance_sheet_quarterly_column_name_flattened_list = [x for sublist in balance_sheet_quarterly_column_name_list for x in sublist]
income_statement_quarterly_column_name_flattened_list = [x for sublist in income_statement_quarterly_column_name_list for x in sublist]

#Create combined dataframes
cash_flow_annual = pd.concat(cash_flow_annual_list, axis=1, ignore_index=True)
cash_flow_annual.columns = cash_flow_annual_column_name_flattened_list

balance_sheet_annual = pd.concat(balance_sheet_annual_list, axis=1, ignore_index=True)
balance_sheet_annual.columns = balance_sheet_annual_column_name_flattened_list

income_statement_annual = pd.concat(income_statement_annual_list, axis=1, ignore_index=True)
income_statement_annual.columns = income_statement_annual_column_name_flattened_list

cash_flow_quarterly = pd.concat(cash_flow_quarterly_list, axis=1, ignore_index=True)
cash_flow_quarterly.columns = cash_flow_quarterly_column_name_flattened_list

balance_sheet_quarterly = pd.concat(balance_sheet_quarterly_list, axis=1, ignore_index=True)
balance_sheet_quarterly.columns = balance_sheet_quarterly_column_name_flattened_list

income_statement_quarterly = pd.concat(income_statement_quarterly_list, axis=1, ignore_index=True)
income_statement_quarterly.columns = income_statement_quarterly_column_name_flattened_list

print(cash_flow_annual)
print(balance_sheet_annual)
print(income_statement_annual)
print(cash_flow_quarterly)
print(balance_sheet_quarterly)
print(income_statement_quarterly)