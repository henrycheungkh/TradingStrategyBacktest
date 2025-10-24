# -*- coding: utf-8 -*-
"""
Created on Sat Mar 25 18:52:00 2023

@author: Henry Cheung
"""

import pandas as pd
import mplfinance as mpf
import numpy as np
from datetime import date, datetime, timedelta
import logging
logging.disable(logging.INFO)
import pytz
import tkinter as tkr
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import pyplot as plt

pd.set_option('display.max_columns', None)

import InvestmentAnalytics.GetHistoricalPriceDataLib as GetHistoricalPriceDataLib
from InvestmentAnalytics.CUDA.TradingMomentReviewer.TradingMomentReviewerCUDALib_SharpeRatio import CUDATradingMomentReviewerSharpeRatio

TradingMomentIndex = 0
TradingMoments_df = None
FullPricesData = None
# FullTradingMomentsDataContext = None

global SORTING_TYPE
SORTING_TYPE = {"Ticker, Date": ['ticker id', 'obs start time id'], "Ticker, Time of Day": ['ticker id', 'TimeInStandardUnit'], "Time of Day, Ticker": ['TimeInStandardUnit', 'ticker id']}

def helloCallBack():
   tkr.messagebox.showinfo("Hello Python", "Hello World")

def ShowTextMessage(message):
   tkr.messagebox.showinfo("", message)
   
# def DisplaySingleDayGraph():
#     data = GetHistoricalPriceDataLib.getHistoricalPriceGraphData(etyStartDate.get(), etyEndDate.get(), vblTimeFrame.get(), [etyTicker.get()])
#     # mpf.plot(data, type='candle', style='charles', volume=True, ylabel='Price')
#     mpf.plot(data, type='candle', style='charles', volume=True, ylabel='Price')

def DisplayDataFrameOnFrame(data, plot_frame, graph_title = '', highlight_from = None, highlight_to = None, highlight_facecolor = 'b', highlight_alpha = 0.3):
    for widget in plot_frame.winfo_children():
        widget.destroy()
    plt.close('all')
    # fig, ax = mpf.plot(data, type='candle', style='charles', volume=True, ylabel='Price', returnfig=True, title=graph_title)
    fig, ax = mpf.plot(data, type='candle', style='yahoo', volume=True, ylabel='Price', returnfig=True, title=graph_title)
    
    if highlight_from is not None and highlight_to is not None:
        # ax[0].axvspan(int(etyObservationPeriod.get())+1,int(etyObservationPeriod.get())+int(etyTradeMomentPeriod.get())+1, facecolor='b', alpha=0.3)
        ax[0].axvspan(highlight_from,highlight_to, facecolor=highlight_facecolor, alpha=highlight_alpha)
    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.draw_idle()
    canvas.get_tk_widget().pack(side=tkr.TOP, fill=tkr.BOTH, expand=1)

def DisplaySingleDayGraphOnFrame(plot_frame, notebook, frame_tab_index = 1):
    global HighlightFrom
    global HighlightTo
    # data = GetHistoricalPriceDataLib.getHistoricalPriceGraphData(etyStartDate.get(), etyEndDate.get(), vblTimeFrame.get(), [etyTicker.get()])
    data = GetHistoricalPriceDataLib.getHistoricalPriceGraphData(etyStartDate.get(), etyEndDate.get(), vblTimeFrame.get(), etyTicker.get().split(","))
    HighlightFrom = None
    HighlightTo = None
    DisplayDataFrameOnFrame(data, plot_frame, graph_title = 'Display Single Day Graph')
    notebook.select(frame_tab_index)
    
def ReSortingMoments(sorting_cols = ['ticker id', 'obs start time id']):
    global TradingMoments_df
    # global SORTING_TYPE

    if TradingMoments_df is not None:
        if len(TradingMoments_df) > 0:
            # TradingMoments_df = TradingMoments_df.sort_values(by=['ticker id', 'obs start time id']).reset_index().drop(columns=['index'])
            # TradingMoments_df = TradingMoments_df.sort_values(by=SORTING_TYPE[vblSortingType.get()]).reset_index().drop(columns=['index'])
            print('To be re sorted by ' + str(sorting_cols))
            TradingMoments_df = TradingMoments_df.sort_values(by=sorting_cols).reset_index().drop(columns=['index'])
    
    
def DisplayHighSharpeRatioMomentsOnFrame(plot_frame, notebook, frame_tab_index = 1):
    global TradingMoments_df
    global FullPricesData
    global TradingMomentIndex
    global PlotHeader
    global HighlightFrom
    global HighlightTo
    global SORTING_TYPE
    # global FullTradingMomentsDataContext
    
    StartDate = datetime.strptime(etyStartDate.get() + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
    EndDate = datetime.strptime(etyEndDate.get() + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
    FullTradingMomentsDataContext, full_data = GetHistoricalPriceDataLib.getListOfTradingMoments(StartDate, EndDate, vblTimeFrame.get(), etyTicker.get().split(","), float(etySharpeRatioThreshold.get()), int(etyTradeMomentPeriod.get()), int(etyObservationPeriod.get()), int(etyAfterMomentPeriod.get()), InstrumentType = vblInstrumentType.get())
    # print('full_data is')
    # print(full_data)
    print('TimeIDMapping is')
    print(FullTradingMomentsDataContext.IntradayPricesData.TimeIDMapping)
    # FullTradingMomentsDataContext.IntradayPricesData.TimeIDMapping.to_csv(r'e:\temp\TimeIDMapping.csv', index=False)
    
    FullPricesData = full_data[['ticker', 'ticker id', 'tDateTime', 'high', 'low', 'open', 'close', 'vol', 'MarketTimeSectionID']]
    FullPricesData = FullPricesData.merge(FullTradingMomentsDataContext.IntradayPricesData.TimeIDMapping[['tDateTime', 'time id']], on='tDateTime', how='left')
    FullPricesData = FullPricesData.rename(columns={"tDateTime": "dates", "vol": "volume"})

    # print('FullPricesData is')
    # print(FullPricesData)
    
    
    TradingMoments_df = CUDATradingMomentReviewerSharpeRatio(float(etySharpeRatioThreshold.get()), float(etyReturnThreshold.get()), int(etyObservationPeriod.get()), int(etyTradeMomentPeriod.get()), int(etyAfterMomentPeriod.get()), FullTradingMomentsDataContext.IntradayPricesData.DataMatrix['TRADES_close_adj'], FullTradingMomentsDataContext.IntradayPricesData.DataMatrix['TimeInStandardUnit'])

# 403 rows
    TradingMoments_df['moment time id'] = TradingMoments_df['obs start time id'] + int(etyObservationPeriod.get())
    TradingMoments_df = TradingMoments_df.merge(FullTradingMomentsDataContext.IntradayPricesData.TimeIDMapping[['TimeInStandardUnit', 'time id']], left_on='moment time id', right_on='time id', how='left')
    # TimeIDToMarketTimeSectionID
    
    # TradingMoments_df = TradingMoments_df.merge(FullTradingMomentsDataContext.IntradayPricesData.TimeIDMapping[['tDateTime', 'time id']], left_on='obs start time id', right_on='time id', how='left')


    if len(TradingMoments_df) <= 0:
        ShowTextMessage("No trading moments found")
    else:
        
        ReSortingMoments()
        # TradingMoments_df = TradingMoments_df.sort_values(by=['ticker id', 'obs start time id']).reset_index().drop(columns=['index'])
        # TradingMoments_df.to_csv(r'e:\temp\TradingMoments_df_before.csv', index=False)

        prev_index = 0
        
        TradingMoments_df['keep'] = 1
        print('TradingMoments_df before is')
        print(TradingMoments_df)
        
        for check_index in range(1, len(TradingMoments_df)):
            # if check_index < 6:
            #     print('check_index = ' + str(check_index) + ', prev_index = ' + str(prev_index) + ', TradingMoments_df.iloc[check_index][\'obs start time id\'] = ' + str(TradingMoments_df.iloc[check_index]['obs start time id']) + ', TradingMoments_df.iloc[prev_index][\'obs start time id\'] = ' + str(TradingMoments_df.iloc[prev_index]['obs start time id']))
            if (TradingMoments_df.iloc[prev_index]['ticker id'] == TradingMoments_df.iloc[check_index]['ticker id']) and (TradingMoments_df.iloc[check_index]['obs start time id'] - TradingMoments_df.iloc[prev_index]['obs start time id'] < int(etyTradeMomentPeriod.get())):
                # TradingMoments_df.iloc[check_index]['keep'] = 0
                TradingMoments_df.at[check_index, 'keep'] = 0
            else:
                prev_index = check_index
                
        TradingMoments_df = TradingMoments_df.loc[TradingMoments_df['keep'] == 1]
        TradingMoments_df = TradingMoments_df.reset_index().drop(columns=['index'])

        ReSortingMoments(SORTING_TYPE[vblSortingType.get()])
        
                
        print('TradingMoments_df after overlap filtered is')
        print(TradingMoments_df)
        # TradingMoments_df.to_csv(r'e:\temp\TradingMoments_df_after.csv', index=False)
        
        TradingMomentIndex = 0
        PlotHeader = 'High Sharpe Ratio'
        HighlightFrom = int(etyObservationPeriod.get())+1
        HighlightTo = int(etyObservationPeriod.get())+int(etyTradeMomentPeriod.get())+1
        DisplayTradingMoment(plot_frame, notebook, frame_tab_index = frame_tab_index)

def DisplayTradingMoment(plot_frame, notebook, frame_tab_index = 1):
    global TradingMoments_df
    global FullPricesData
    global TradingMomentIndex
    global PlotHeader
    global HighlightFrom
    global HighlightTo
    # global FullTradingMomentsDataContext

    # data = df_Price[['tDateTime', 'high', 'low', 'open', 'close', 'vol']]
    
    # data = data.rename(columns={"tDateTime": "dates", "vol": "volume"})
    # data.index = pd.DatetimeIndex(data['dates'])
    
    ticker_id = TradingMoments_df.iloc[TradingMomentIndex]['ticker id']
    time_id = TradingMoments_df.iloc[TradingMomentIndex]['obs start time id']
    
    # print('ticker id is ' + str(ticker_id) + ' and time_id is ' + str(time_id))
    
    ThisMomentData = FullPricesData.loc[(FullPricesData['ticker id'] == ticker_id) & (FullPricesData['time id'] >= time_id) & (FullPricesData['time id'] <= time_id + int(etyObservationPeriod.get()) + int(etyTradeMomentPeriod.get()) + int(etyAfterMomentPeriod.get()) )]
   
    # print('ThisMomentData is')
    # print(ThisMomentData)
    ticker_name = ThisMomentData.iloc[0]['ticker']
    date_string = ThisMomentData.iloc[int(etyObservationPeriod.get())]['dates'].strftime("%Y-%m-%d")
    
    # FullTradingMomentsDataContext.IntradayPricesData.TimeIDMapping.loc[FullTradingMomentsDataContext.IntradayPricesData.TimeIDMapping['time id']]
    
    ThisMomentData = ThisMomentData[['dates', 'high', 'low', 'open', 'close', 'volume']]
    ThisMomentData.index = pd.DatetimeIndex(ThisMomentData['dates'])
    
    DisplayDataFrameOnFrame(ThisMomentData, plot_frame, graph_title = ticker_name + ' - ' + date_string + ' - ' + PlotHeader + ' - ' + str(TradingMomentIndex) + '/' + str(len(TradingMoments_df)), highlight_from = HighlightFrom, highlight_to = HighlightTo)
    notebook.select(frame_tab_index)
    etyTradingMomentIDText.set(str(TradingMomentIndex))
    
def PrevTradingMoment(plot_frame, notebook, frame_tab_index = 1):
    global TradingMoments_df
    global TradingMomentIndex
    

    if int(etyTradingMomentIDText.get()) > 0:
        TradingMomentIndex = int(etyTradingMomentIDText.get()) - 1
    # if TradingMomentIndex > 0:
        # TradingMomentIndex = TradingMomentIndex - 1
        DisplayTradingMoment(plot_frame, notebook, frame_tab_index = frame_tab_index)
        
def NextTradingMoment(plot_frame, notebook, frame_tab_index = 1):
    global TradingMoments_df
    global TradingMomentIndex
    
    
    if int(etyTradingMomentIDText.get()) < len(TradingMoments_df):
        TradingMomentIndex = int(etyTradingMomentIDText.get()) + 1
    # if TradingMomentIndex < len(TradingMoments_df):
        # TradingMomentIndex = TradingMomentIndex + 1
        DisplayTradingMoment(plot_frame, notebook, frame_tab_index = frame_tab_index)

    
def FirstTradingMoment(plot_frame, notebook, frame_tab_index = 1):
    global TradingMomentIndex
    
    TradingMomentIndex = 0
    DisplayTradingMoment(plot_frame, notebook, frame_tab_index = frame_tab_index)

def LastTradingMoment(plot_frame, notebook, frame_tab_index = 1):
    global TradingMoments_df
    global TradingMomentIndex
    
    TradingMomentIndex = len(TradingMoments_df) - 1
    DisplayTradingMoment(plot_frame, notebook, frame_tab_index = frame_tab_index)

# def JumpToTradingMoment():
#     print(etyTradingMomentIDText.get())
#     return True

def JumpToTradingMoment(new_TradingMomentIndex, plot_frame, notebook, frame_tab_index = 1):
    # print(etyTradingMomentIDText.get())
    global TradingMoments_df
    global TradingMomentIndex
    
    if TradingMoments_df is not None:
        if len(TradingMoments_df) > 0:
            # TradingMomentIndex = int(etyTradingMomentIDText.get())
            TradingMomentIndex = new_TradingMomentIndex
            DisplayTradingMoment(plot_frame, notebook, frame_tab_index = frame_tab_index)

def ExportSingleJPGFile(filepath):
    plt.savefig(filepath, format='jpg')


def ExportSingleJPGFiles(filepath, plot_frame, notebook):
    global TradingMoments_df
    global TradingMomentIndex
    
    if TradingMoments_df is not None:
        if len(TradingMoments_df) > 0:
            for TradingMomentIndex in range(len(TradingMoments_df)):
                substituted_filepath = filepath.replace("xxxxx", str(TradingMomentIndex).zfill(5))
                JumpToTradingMoment(TradingMomentIndex, plot_frame, notebook)
                ExportSingleJPGFile(substituted_filepath)
                
    ShowTextMessage('JPG Files exported')


tk = tkr.Tk()

AppWidth = tk.winfo_screenwidth() - 20
AppHeight = tk.winfo_screenheight() - 100

tk.geometry(str(AppWidth) + "x" + str(AppHeight))
tk.title("Trading Moment Reviewer")

# btnHello = tkr.Button(tk, text ="Hello", command = helloCallBack)
# btnHello.place(x=50, y=10)

# btnDisplayStartDate = tkr.Button(tk, text ="Message Start Date", command = lambda:ShowTextMessage(etyStartDate.get()))
# btnDisplayStartDate.place(x=100, y=10)

lblStartDate = tkr.Label(tk, text = 'Start Date')
lblStartDate.place(x=10, y=50, height=25)

etyStartDate = tkr.Entry(tk)
# etyStartDate.insert(-1, '2021-11-26')
etyStartDate.insert(-1, '2022-01-01')
etyStartDate.place(x=100, y=50, height=25)

lblEndDate = tkr.Label(tk, text = 'End Date')
lblEndDate.place(x=10, y=100, height=25)

etyEndDate = tkr.Entry(tk)
# etyEndDate.insert(-1, '2021-11-26')
etyEndDate.insert(-1, '2022-12-31')
etyEndDate.place(x=100, y=100, height=25)

lblTimeFrame = tkr.Label(tk, text = 'TimeFrame')
lblTimeFrame.place(x=10, y=150, height=25)

vblTimeFrame = tkr.StringVar(tk)
vblTimeFrame.set("1 min") # default value

OpmTimeFrame = tkr.OptionMenu(tk, vblTimeFrame, "1 min", "10 secs", "5 mins")
OpmTimeFrame.place(x=100, y=150, height=25)

lblInstrumentType = tkr.Label(tk, text = 'Instrument Type')
lblInstrumentType.place(x=10, y=200, height=25)

vblInstrumentType = tkr.StringVar(tk)
vblInstrumentType.set("Futures") # default value

OpmInstrumentType = tkr.OptionMenu(tk, vblInstrumentType, "Futures", "Crypto")
OpmInstrumentType.place(x=110, y=200, height=25)

lblTicker = tkr.Label(tk, text = 'Ticker')
lblTicker.place(x=10, y=250, height=25)

etyTicker = tkr.Entry(tk)
etyTicker.insert(-1, 'RTY')
etyTicker.place(x=100, y=250, height=25, width=50)

tab_parent = ttk.Notebook(tk)
tab_parent.place(x=300, y=0, width=AppWidth-400, height=AppHeight-150)

tabMomentsList = ttk.Frame(tab_parent)
tab_parent.add(tabMomentsList, text="Other Criteria")

tabKGraph = ttk.Frame(tab_parent)
tab_parent.add(tabKGraph, text="K Graph")

tabStat = ttk.Frame(tab_parent)
tab_parent.add(tabStat, text="Statistics")

btnSingleDayGraph = tkr.Button(tk, text ="Display Single Day Graph", command = lambda:DisplaySingleDayGraphOnFrame(tabKGraph, tab_parent))
btnSingleDayGraph.place(x=10, y=300)

lblSharpeRatioThreshold = tkr.Label(tk, text = 'Trade Moment Min Sharpe Ratio')
lblSharpeRatioThreshold.place(x=10, y=350, height=25)

etySharpeRatioThreshold = tkr.Entry(tk)
etySharpeRatioThreshold.insert(-1, '1.5')
etySharpeRatioThreshold.place(x=230, y=350, height=25, width=50)

lblReturnThreshold = tkr.Label(tk, text = 'Trade Moment Min Abs Return')
lblReturnThreshold.place(x=10, y=400, height=25)

etyReturnThreshold = tkr.Entry(tk)
etyReturnThreshold.insert(-1, '0.005')
etyReturnThreshold.place(x=230, y=400, height=25, width=50)

lblTradeMomentPeriod = tkr.Label(tk, text = 'Trade Moment Period')
lblTradeMomentPeriod.place(x=10, y=450, height=25)

etyTradeMomentPeriod = tkr.Entry(tk)
etyTradeMomentPeriod.insert(-1, '5')
etyTradeMomentPeriod.place(x=150, y=450, height=25, width=50)

lblTradeMomentPeriodCandle = tkr.Label(tk, text = 'Candles')
lblTradeMomentPeriodCandle.place(x=210, y=450, height=25)

lblObservationPeriod = tkr.Label(tk, text = 'Observation Period')
lblObservationPeriod.place(x=10, y=500, height=25)

etyObservationPeriod = tkr.Entry(tk)
etyObservationPeriod.insert(-1, '50')
etyObservationPeriod.place(x=150, y=500, height=25, width=50)

lblObservationPeriodCandle = tkr.Label(tk, text = 'Candles')
lblObservationPeriodCandle.place(x=210, y=500, height=25)

lblAfterMomentPeriod = tkr.Label(tk, text = 'After Moment Period')
lblAfterMomentPeriod.place(x=10, y=550, height=25)

etyAfterMomentPeriod = tkr.Entry(tk)
etyAfterMomentPeriod.insert(-1, '10')
etyAfterMomentPeriod.place(x=150, y=550, height=25, width=50)

lblAfterMomentPeriodCandle = tkr.Label(tk, text = 'Candles')
lblAfterMomentPeriodCandle.place(x=210, y=550, height=25)

btnDisplayHighSharpeRatioMoment = tkr.Button(tk, text ="Display High Sharpe Ratio Moments", command = lambda:DisplayHighSharpeRatioMomentsOnFrame(tabKGraph, tab_parent))
btnDisplayHighSharpeRatioMoment.place(x=10, y=600)


btnFirstTradingMoment = tkr.Button(tk, text =" |< ", command = lambda:FirstTradingMoment(tabKGraph, tab_parent))
btnFirstTradingMoment.place(x=350, y=750)

btnPrevTradingMoment = tkr.Button(tk, text =" << ", command = lambda:PrevTradingMoment(tabKGraph, tab_parent))
btnPrevTradingMoment.place(x=400, y=750)


etyTradingMomentIDText = tkr.StringVar()
# etyTradingMomentID = tkr.Entry( tk, textvariable=etyTradingMomentIDText, validate="focusout", validatecommand=JumpToTradingMoment )
etyTradingMomentID = tkr.Entry( tk, textvariable=etyTradingMomentIDText, validate="focusout", validatecommand=lambda:JumpToTradingMoment(int(etyTradingMomentIDText.get()), tabKGraph, tab_parent) )
etyTradingMomentIDText.set( "" )

# etyTradingMomentIDText.trace("w", lambda name, index, mode, sv=sv: callback(sv))

# etyTradingMomentID = tkr.Entry(tk)
# etyTradingMomentID.insert(-1, '')
etyTradingMomentID.place(x=450, y=750, height=25, width=50)


btnNextTradingMoment = tkr.Button(tk, text =" >> ", command = lambda:NextTradingMoment(tabKGraph, tab_parent))
btnNextTradingMoment.place(x=520, y=750)

btnLastTradingMoment = tkr.Button(tk, text =" >| ", command = lambda:LastTradingMoment(tabKGraph, tab_parent))
btnLastTradingMoment.place(x=570, y=750)

lblSortingType = tkr.Label(tk, text = 'Instrument Type')
lblSortingType.place(x=350, y=800, height=25)

vblSortingType = tkr.StringVar(tk)
vblSortingType.set("Ticker, Date") # default value

OpmSortingType = tkr.OptionMenu(tk, vblSortingType, "Ticker, Date", "Ticker, Time of Day", "Time of Day, Ticker")
OpmSortingType.place(x=450, y=800, height=25)

# btnReSortTradingMoment = tkr.Button(tk, text ="Re-sort", command = ReSortingMoments)
btnReSortTradingMoment = tkr.Button(tk, text ="Re-sort", command = lambda:ReSortingMoments(SORTING_TYPE[vblSortingType.get()]))
btnReSortTradingMoment.place(x=600, y=800)

etyJPGExportFileName = tkr.Entry(tk)
etyJPGExportFileName.insert(-1, r'e:\temp\Exported JPG File.jpg')
etyJPGExportFileName.place(x=750, y=750, height=25, width=500)

btnJPGExportFileName = tkr.Button(tk, text ="Export JPG File", command = lambda:ExportSingleJPGFile(etyJPGExportFileName.get()))
btnJPGExportFileName.place(x=1300, y=750)

etyJPGExportFileNames = tkr.Entry(tk)
etyJPGExportFileNames.insert(-1, r'e:\temp\Exported JPG Files xxxxx.jpg')
etyJPGExportFileNames.place(x=750, y=800, height=25, width=500)

btnJPGExportFileNames = tkr.Button(tk, text ="Export JPG Files", command = lambda:ExportSingleJPGFiles(etyJPGExportFileNames.get(), tabKGraph, tab_parent))
btnJPGExportFileNames.place(x=1300, y=800)

tk.mainloop()





