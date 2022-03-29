# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 18:59:16 2022

@author: Leo
"""

from os import scandir, getcwd, path
import csv
import datetime as dt
import pickle
import pandas as pd
import yfinance as yf


def pop_watchlist(open_path=None, open_file=None):
    """populate and return watchlist from csv file at given destination path"""

    # default watchlist is returned when no file is specified
    if open_path is None or open_file is None:
        return ["SPY", "QQQ", "DIA", "UVXY"]
    
    with open(path.join(open_path, open_file)) as file:
        watchlist = []
        for row in csv.reader(file):   
            watchlist.append(row[0])
   
    watchlist.sort()
    
    return watchlist


def update_1m_28day(ticker, write_path, weeks=4, new_ticker=False):
    """Use yfinance to download ticker data and write to csv file"""
    
    data_path = path.join(write_path, ticker)
    total_data = pd.DataFrame()
    num_weeks = weeks + 1
    
    for n in range(1, num_weeks):
        start = dt.date.today() - dt.timedelta(weeks=n)
        end = start + dt.timedelta(days=7)
        data = yf.download(ticker, start, end, interval="1m")
        data = data.drop(data.tail(1).index)
        frames = [data, total_data]
        total_data = pd.concat(frames)
        
    print(f"{ticker} data downloaded from Yahoo Finance")
    
    if new_ticker == False:
        old_data = pd.read_csv(f"{data_path}-1m.csv", 
                               index_col="Datetime")
        update_data = pd.concat([old_data, total_data])
        update_data.to_csv(f"{data_path}-1m.csv")
        print(f"{ticker} data written to csv file\n")
    else:
        total_data.to_csv(f"{data_path}-1m.csv")
        print(f"{ticker} data written to csv file\n")

    return


def download_ticker_data(watchlist=None, file_path=getcwd(), weeks=4):
    """
    
    Download a week's worth of 1m data at a time from Yahoo finance for up 
    to 4 weeks total and update to a csv file. If ticker is new then download
    full 4 weeks and write a new csv file to write_path.
    Assumed filenames of csv files is "TICK-1m.csv""
    """
    
    if watchlist is None:
        watchlist = pop_watchlist()
    
    # obtain ticker and file names to include any existing
    file_list = {file.name.split("-")[0]: file.name for file in scandir(file_path) 
                 if file.is_file()}  
    
    for ticker in watchlist:
        if ticker in file_list.keys():
            print(ticker)
            fname = file_list[ticker]
            data_path = path.join(file_path, fname)
            file_check = pd.read_csv(data_path, nrows=1)
            
            # check for "Datetime" column commonly dropped by yfinance and 
            # replace if unnamed
            if "Datetime" not in file_check.columns:
                file_check = pd.read_csv(data_path)
                file_check.rename(columns={"Unnamed: 0":"Datetime"}, 
                                  inplace=True)
                file_check.to_csv(data_path, index=False)
    
            update_1m_28day(ticker, file_path, weeks)
           
        else:
            # if new ticker obtain the max allowed 4 weeks for 1m bars
            print(f"New: {ticker}")
            update_1m_28day(ticker, file_path, 4, True)
            
    return "All data downloaded"


def pop_data_dict(file_path=getcwd(), data=None, ticker_dates=None):
    """
    
    Open all relevant files and populate data dictionary with ticker dataframes
    and change Datetime to real Timestamp object from string.
    """

    if data is None:
        data = {}
    if ticker_dates is None:
        ticker_dates = {}
        
    # obtain new file list to include any new files/tickers
    file_list = [file for file in scandir(file_path) if file.is_file()]
   
    for file in file_list:
        ticker = file.name.split("-")[0]
        new_data_path = path.join(file_path, file.name)
        print(ticker)
        
        # determine the most recently updated data
        if ticker in ticker_dates.keys():
            recent_index = ticker_dates[ticker][-1][-1]
        else:
            recent_index = 0
            
        new_data = pd.read_csv(new_data_path)
        new_data = new_data[recent_index:]
        
        if len(new_data) < 2:
            pass
        else:
            if ticker in data.keys():
                if "Datetime" not in data[ticker].columns:
                    new_data.rename(columns={"Unnamed: 0": "Datetime"}, 
                                    inplace=True)
                    
                # convert datetime strings to proper datetime objects
                new_data["Datetime"] = new_data["Datetime"].apply(
                                       lambda x: dt.datetime.strptime(
                                                   x[:16], "%Y-%m-%d %H:%M")
                                       )
                
                new_data = new_data.sort_values(by="Datetime", ignore_index=True)
                new_data = new_data.drop_duplicates(subset=["Datetime"], keep="first")
                new_data = new_data.reset_index(drop=True)
                data[ticker] = pd.concat([data[ticker], new_data])
            
            else:
                if "Datetime" not in new_data.columns:
                    new_data.rename(columns={"Unnamed: 0": "Datetime"}, inplace=True)
                
                # convert datetime strings to proper datetime objects
                new_data["Datetime"] = new_data["Datetime"].apply(
                                       lambda x: dt.datetime.strptime(
                                                   x[:16], "%Y-%m-%d %H:%M")
                                       )
                
                new_data = new_data.sort_values(by="Datetime", ignore_index=True)
                new_data = new_data.drop_duplicates(subset=["Datetime"], keep="first")
                new_data = new_data.reset_index(drop=True)
                data[ticker] = new_data
        
    return data


def pop_ticker_dates(file_path=getcwd(), data=None, ticker_dates=None):
    """
    
    Populate a dictionary containing a list of lists that holds each 
    month-date-year triplet and corresponding index pairs for market open (9:30am) 
    and close (4:00pm) daily timestamps for the relevant locations in the 
    dataframes.
    """
    
    if data is None:
        print("\nNo data supplied: please pass a dictionary of dataframes "
              + "as an argument or use the pop_data_dict() function")
        return
    
    if ticker_dates is None:
        ticker_dates = {}
        
    # obtain new file list to include any new files/tickers
    file_list = [file for file in scandir(file_path) if file.is_file()]
    
    for file in file_list:
        ticker = file.name.split("-")[0]
        print(ticker)
        
        # determine the most recently updated data
        if ticker in ticker_dates.keys():
            recent_index = ticker_dates[ticker][-1][-1]
        else:
            recent_index = 0

        new_data = data[ticker][recent_index:]
        
        if len(new_data) < 2:
            # log error?
            pass
        else:
            begin_index = new_data.index[0]
            end_index = new_data.index[-1]
            dates = []
            month = new_data["Datetime"][begin_index].month
            day = new_data["Datetime"][begin_index].day
            year = new_data["Datetime"][begin_index].year
            start = begin_index
            num_days = 0
            dates.append([month, day, year, start])
            
            # iterate through dataframe and separate into different days
            for i in range(begin_index+1, end_index):
                if new_data["Datetime"][i].date() != new_data["Datetime"][i-1].date():
                    start = i
                    month = new_data["Datetime"][i].month
                    day = new_data["Datetime"][i].day
                    year = new_data["Datetime"][i].year
                    dates.append([month, day, year, start])
                    dates[num_days].append(i)
                    num_days += 1
        
            # adding final index value for final day
            dates[-1].append(end_index+1)
            
            if ticker in ticker_dates.keys():
                ticker_dates[ticker].extend(dates)
            else:
                ticker_dates[ticker] = dates 
    
    return ticker_dates


def load_pickles(file_path, data_name, ticker_dates_name):
    """load and return pickle files of previously stored data and ticker_dates"""
    
    data_in = path.join(file_path, data_name)
    file_in = open(data_in, "rb")
    data = pickle.load(file_in)
    
    dates_in = path.join(file_path, ticker_dates_name)
    file_in = open(dates_in, "rb")
    ticker_dates = pickle.load(file_in)
    
    return data, ticker_dates


def save_pickles(file_path, data, data_name, ticker_dates, ticker_dates_name):
    """Save/pickle data and ticker_dates for future use"""
    
    data_out = path.join(file_path, data_name)
    filehandler = open(data_out, "wb")
    pickle.dump(data, filehandler)
    filehandler.close()
    
    dates_out = path.join(file_path, ticker_dates_name)
    filehandler = open(dates_out, "wb")
    pickle.dump(ticker_dates, filehandler)
    filehandler.close()
    
    return

