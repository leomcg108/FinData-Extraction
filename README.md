# FinData-Extraction
> Easily download and update US stock market intraday 1m data with Yahoo Finance

This project addresses some of the limitations present in Yahoo Finance’s historical data requests through the yfinance API, namely that 1 minute increment of intraday US equities OHLCV (open, high, low, close, volume) data are only available for the previous 30 days and that each individual request will only return 7 day’s worth of data. 

In practice this project is a simple method to download and concatenate csv files for the 4 previous weeks with existing csv files of the same stock. In this way an update every 4 weeks willl allow for accumulation of fine granularity intraday data for your own personal storage and backtesting. 

Additionally, this project will output a dictionary of dataframes and a dictionary of indices for the corresponding open and close times for each ticker for each day allowing for faster lookups of price data.

## Table of Contents
* Features
* Dependencies
* Example
* Speed Comparison
* Future Work

## Features
* Populate a watchlist of tickers from a user-defined csv file
* Use this watchlist to download for each ticker the previous 1 to 4 weeks worth of 1 minute OHLCV intraday data and add to existing csv file
* Create or modify a dictionary with tickers as keys and their dataframes as values. The dataframes contain OHLCV data with timestamp objects derived from the string literals provided by Yahoo Finance. New data is added to existing dataframes
* Populate a dictionary of tickers as keys and as values a list of dates and the corresponding indices for the open (9:30am EST) and close (4:00pm EST) timestamps for each day present in the ticker’s dataframes
* Allows for quick and easy updating of stored stock market dataframes
* Data structure allows for rapid backtesting of strategies e.g. 1 year’s worth of 1m data for a basket of 500 stocks tested in 30 seconds
* Plot stock prices for a given ticker over a specified date range
* Downcast dataframe dictionary to reduce memory usage
* Check downloaded data for missing days and missing minutes

## Dependencies
* python
* pandas
* yfinance
* matplotlib

## Example
Create an instance of the class `FinDataExtract` and define a path to access or save csv files
```python
>>> fde = FinDataExtract()
>>> file_path = ".\\Watchlist\\Test\\"
>>> fde.set_file_path(file_path)
>>> fde.file_path
".\\Watchlist\\Test\\"
```

The `pop_watchlist()` method will return a default list of the major indices most popular ETFs i.e.  SPY, QQQ, DIA, UVXY. Otherwise a watchlist file can be specified with the `watchlist_path` argument.

```python
# populate watchlist from a csv file
>>> watchlist = fde.pop_watchlist()
>>> print(watchlist)

['SPY', 'QQQ', 'DIA', 'UVXY']
```

Use `download_ticker_data()` to download 4 weeks of 1 minute intraday data for the specified watchlist and save in individual csv files at the previously specified `file_path`.

```python
# specify the number of weeks for which to update watchlist (max is 4, min is 1). For new tickers the default is 4 weeks
>>> weeks = 4
>>> fde.download_ticker_data(weeks)

New: SPY
[*********************100%***********************]  1 of 1 completed
[*********************100%***********************]  1 of 1 completed
[*********************100%***********************]  1 of 1 completed
[*********************100%***********************]  1 of 1 completed
SPY data downloaded from Yahoo Finance
SPY data written to csv file
.
.
.

'All data downloaded'
```

`pop_data_dict()` will update a data dictionary with the newly downloaded data if `data` and `ticker_dates` dictionaries have been passed as arguments during class instantiation. Otherwise a new `data` dictionary will be made from the csv files at `file_path`.  Datetime strings will be converted to timestamp objects also.

```python
>>> fde.pop_data_dict()
>>> data = fde.data

>>> data["SPY"].head()

             Datetime        Open        High  ...       Close   Adj Close   Volume
0 2022-02-25 09:30:00  429.609985  429.679993  ...  429.089996  429.089996  4895990
1 2022-02-25 09:31:00  429.079987  429.179993  ...  428.907013  428.907013   382172
2 2022-02-25 09:32:00  428.920013  429.510010  ...  429.170013  429.170013   449220
3 2022-02-25 09:33:00  429.190002  430.400085  ...  430.394989  430.394989   416130
4 2022-02-25 09:34:00  430.429993  431.059998  ...  430.920013  430.920013   476738


# Datetime column is converted to proper timestamp from string

>>> type(data["SPY"]["Datetime"][0])

pandas._libs.tslibs.timestamps.Timestamp
```

The `ticker_dates` structure can be used to quickly return the open and close indices for that day e.g. [month, day, year, open index, close index].

`fde.ticker_dates` will be updated with new dates from the `fde.data` dataframes or built from scratch if nothing was passed during instantiation.

```python
>>> fde.pop_ticker_dates()

DIA
QQQ
SPY
UVXY

>>> ticker_dates = fde.ticker_dates

>>> ticker_dates["SPY"][0]
[2, 25, 2022, 0, 390]
# [month, day, year, open index, close index]

>>> start_index = ticker_dates["SPY"][10][3]

>>> data["SPY"].iloc[start_index]

Datetime     2022-03-11 09:30:00
Open                  428.119995
High                  428.600006
Low                   428.079987
Close                 428.540009
Adj Close             428.540009
Volume                   3272859
Name: 3890, dtype: object
```
Verify that all the requested data was in fact downloaded correctly by using the `pde.verify_data()` method. This method returns a dictionary with ticker keys and a list of dates that are not in the dataframe. The `minute_check` flag is set to False by default but when set to True will return a dictionary of tickers and a list of tuples with dates and the number of missing minutes.

```python
>>> day_check, minute_test = fde.verify_data(minute_check=True)
>>> print(day_check)
# Example output of missing days of data
{'TQQQ': datetime.date(2022, 2, 28),
  datetime.date(2022, 3, 4),
  datetime.date(2022, 3, 1),
  datetime.date(2022, 3, 2)]}

>>> print(minute_test)
# Days with missing minutes and the number of missing minutes
{'DIA': [(datetime.date(2022, 3, 9), 7),
  (datetime.date(2022, 3, 10), 2),
  (datetime.date(2022, 3, 17), 1),
  (datetime.date(2022, 3, 22), 1)
.
.
.
```
In certain cases perhaps it may be simply better to have data for a single ticker organised by days. The `data_by_date` date method will, for a specified ticker, return a dictionary with key dates (as datetime objects) and values as the corresponding day’s data in the form of a dataframe.


```python

>>> dia = fde.data_by_date("DIA")
>>> dia[dt.date(2022, 3, 14)].reset_index(drop=True).head(2)

             Datetime        Open        High  ...       Close   Adj Close    Volume
0 2022-03-14 09:30:00  331.750000  332.519989  ...  332.130005  332.130005  213090.0
1 2022-03-14 09:31:00  332.170013  332.380005  ...  332.179993  332.179993   23337.0

[2 rows x 7 columns]
```
Reduce the burden on system memory by downcasting the numerical OHLC values from float64 to float32 with the `downcast_data` method.

```python
>>> dia[dt.date(2022, 3, 14)].memory_usage(deep=True)
Index         132
Datetime     3120
Open         3120
High         3120
Low          3120
Close        3120
Adj Close    3120
Volume       3120
dtype: int64

>>> fde.downcast_data(dia)
>>> dia[dt.date(2022, 3, 14)].memory_usage(deep=True)
Index         132
Datetime     3120
Open         1560
High         1560
Low          1560
Close        1560
Adj Close    1560
Volume       3120
dtype: int64

```

You can also use `fde.slice_data()` to return a slice of the dataframe for a ticker between two dates. Defaults for `start_date` and `end_date` are the start and end of the relevant dataframe.

```python
>>> temp_data = slice_data(ticker="SPY", start_date="2022-03-14", end_date="2022-03-18")

>>> temp_data.head(2)

             Datetime        Open        High  ...       Close   Adj Close   Volume
0 2022-03-14 09:30:00  420.890015  421.970001  ...  421.489990  421.489990  3008304
1 2022-03-14 09:31:00  421.500000  421.920013  ...  421.779999  421.779999   389313

[2 rows x 7 columns]

>>> temp_data.tail(2)

                Datetime        Open  ...   Adj Close   Volume
1945 2022-03-18 15:58:00  444.329987  ...  444.220001   694944
1946 2022-03-18 15:59:00  444.220001  ...  444.470001  2761408

[2 rows x 7 columns]
```

`plot_data` is a convenient way to plot a dataframe slice for a date range for a given ticker and specified data column.

```python
>>> plot_data(ticker="QQQ", start_time="2022-03-14", end_time=None, plot_series="Close")

Data slice for QQQ
Close-data plotted for QQQ
```
![QQQ Close plot](https://user-images.githubusercontent.com/102587512/161250963-29b20300-d9c3-4766-b438-6b010fc3fb76.png)

```python
>>> plot_data(ticker="SPY", start_time="2022-03-18", end_time="2022-03-18", plot_series="Volume")

Data slice for SPY
Volume-data plotted for SPY
```
![SPY Volume plot](https://user-images.githubusercontent.com/102587512/161251038-5b8ffe01-5690-44fd-8224-91cd9beadcfa.png)

When you’re finished working with your data you can serialize it by using the `save_pickles()` function.

```python
data_name = “full_data.pickle”
ticker_dates_name = “all_ticker_dates.pickle”

save_pickles(pickle_path=".//Example", data_name, ticker_dates_name)
```
Reload in your next session with `load_pickles()`

```python
data_name = “full_data.pickle”
ticker_dates_name = “all_ticker_dates.pickle”

data, ticker_dates = load_pickles(pickle_path=".//Example", data_name, ticker_dates_name)
```

## Speed Comparison
What are the benefits of using the `ticker_dates` as a data structure in addition to the ticker dataframes? The main benefit of using this structure is a speed improvement for specific datetime lookups and generating slices of those dataframes. Take the example below which outlines the difference in time to produce a dataframe slice of 14th March 2022 from SPY data using various methods.

```python
from timeit import timeit

# Given datetime objects as reference return the slice for that day’s dataframe

start_date_str = "2022-03-14 09:30"
end_date_str = "2022-03-14 15:59"
```
### Datetime lookup method
Total time for preprocessing step to define `start_date` and `end_date` from given strings is **15.16 µs**
(for detail on this step see section below)

Define `temp_data` as a slice generated by comparing timestamps from the Datetime column of the dataframe to `start_date` and `end_date`
```python
%timeit temp_data = data[ticker][data[ticker].index[data[ticker].Datetime == start_date[0]:data[ticker].index[data[ticker].Datetime == end_date][0]]
```

Time taken: **308 µs** ± 2.71 µs

### `ticker_dates` lookup method

Total time for preprocessing step to define `dates_index` is **10.16 µs**
(for details on this step see section below)

```python
%timeit temp_data = data[ticker][ticker_dates[ticker][dates_index][3]:ticker_dates[ticker][dates_index][4]]
```
Time taken: **22.8 µs** ± 96.6 ns

### Integer lookup
For reference here is the time taken to generate the same `temp_data` slice with known integer values for the relevant indices.
```python
%timeit temp_data = data[ticker][3890:4280]
```
Time taken: **22.1 µs** ± 99 ns

You can see this is only marginally faster than the `ticker_dates` lookup method. This is due to the time needed to produce `dates_index` from the given string.

Therefore:
**Speed improvement = 308 / 23 = 13.26 times faster**

Using the `ticker_dates` lookup method seems to give at least an order of magnitude speed boost in terms of performance over the datetime object lookup method. This is essentially a lower bound on performance improvement as for larger dataframes datetime lookup will take longer but the `ticker_dates` method will not change appreciably.

### Preprocessing steps
Analysis of time taken to convert given datetime strings to the necessary indices to return the slice for that day’s dataframe

**Datetime lookup method**
```python
>>> start_date_str = "2022-03-14 09:30"
>>> end_date_str = "2022-03-14 15:59"

>>> %timeit start_date = dt.datetime.strptime(start_date_str, "%Y-%m-%d %H:%M")
7.55 µs ± 61.7 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)

>>> %timeit end_date = dt.datetime.strptime(end_date_str, "%Y-%m-%d %H:%M")
7.61
 µs ± 59 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)
```

Total preprocessing time: 7.55 + 7.61 = **15.16 µs**

**`ticker_dates` lookup method**
```python
>>> start_date_str = "2022-03-14 09:30"

>>> %timeit start_date = dt.datetime.strptime(start_date_str, "%Y-%m-%d %H:%M")
7.55 µs ± 61.7 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)

>>> %timeit start_list = [start_date.month, start_date.day, start_date.year]
107 ns ± 0.966 ns per loop (mean ± std. dev. of 7 runs, 10000000 loops each)

>>> %timeit dates_index = [ticker_dates[ticker].index(x) for x in ticker_dates[ticker] if x[:3] == start_list][0]
2.88 µs ± 30.8 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)
```

Total preprocessing time = 7.55 µs + 107 ns + 2.88 µs + 66.5 ns
Total preprocessing time = **10.60 µs**


However if the day index is already known or we just care about iterating through all days then lookup is very fast
```python
>>> dates_index = 10
>>> %timeit temp_index = ticker_dates[ticker][dates_index][3]
65.8 ns ± 0.229 ns per loop (mean ± std. dev. of 7 runs, 10000000 loops each)
```
Speed improvement for preprocessing: 15 / 0.06 = 250 times faster


## Future Work
- ~~Add function to return slices of data between two specified datetimes~~
- ~~Add plotting function for defined slices~~
- ~~Verify data has been downloaded correctly and return a list of missing days~~
- ~~Compress data function to limit memory usage for large data sets~~
- Add support for different timeframes, e.g. 5 minute bar data
- Add options for MultiIndex in pandas dataframes to replace ticker_dates

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
