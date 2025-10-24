# -*- coding: utf-8 -*-
"""
Created on Tue Apr  6 15:37:06 2021

@author: Henry Cheung
"""

import pycuda.driver as cuda
import pycuda.autoinit
from pycuda.compiler import SourceModule
import math
import pandas as pd

import InvestmentAnalytics.CUDA.CUDAPathSetting
import InvestmentAnalytics.Config as Config

import numpy as np


TOTAL_TIME_IN_STD_UNIT_PER_DAY = {"1 min":24*60, "10 secs":24*60*60}

def AppendListToDF(original_df, column_name, lst):
    if isinstance(lst[0], list):
        col_name_list = []
        for i in range(len(lst[0])):
            col_name_list.append(column_name+' '+str(i))
    else:
        col_name_list = [column_name]
    df = pd.DataFrame(lst, columns =col_name_list)
    df['Dummy'] = 1
    return original_df.merge(df, on='Dummy')

def InitialiseScenarioMatrix(ticker_count, scenario_labels_dict):
    ticker_list = []
    for i in range(ticker_count):
        ticker_list.append(i)
    scenario_df = pd.DataFrame(ticker_list,columns =['ticker id'])
    scenario_df['Dummy'] = 1
    for key in scenario_labels_dict:
        scenario_df = AppendListToDF(scenario_df, key, scenario_labels_dict[key])

    scenario_df.drop(columns=['Dummy'], inplace=True)

    # scenario_df.to_csv(r'G:\TradeAnalysisProject\temp\scenario_df.csv', index=False)
    scenario_matrix = scenario_df.to_numpy().astype(np.float32)
    return scenario_matrix.copy(order="C")

# def CUDARangeTradeOnSpecificPastTimeRangeStrategy(close_price_matrix, high_price_matrix, low_price_matrix, date_id_matrix, time_std_unit_matrix, StartTimeInStdUnit, EndTimeInStdUnit, TimeIntervalInStdUnit, ObsPeriodMovementThreshold = [0], ObsPeriodMovementRange = 0, StopLossPerTrade = 0, TakeProfitPerTrade = 0, ObsDateIDOffset = 0, TradeEntryDateIDOffset = 0, block_cutting_dimension = "Time Dimension", InitialResultCacheSize = None, TimeFrame = "1 min", GPU_CORE_BLOCK_SIZE = 32*32):
def CUDARangeTradeOnSpecificPastTimeRangeStrategy(close_price_matrix, high_price_matrix, low_price_matrix, date_id_matrix, time_std_unit_matrix, StartTimeInStdUnit, EndTimeInStdUnit, TimeIntervalInStdUnit, RangeBoundaryTimeIntervalInStdUnit, MinRangeTimeWidthInStdUnit, MaxBackdateTimePeriodInStdUnit, MinBackdateTimePeriodInStdUnit, MinRangeWidth = [0.01], MaxRangeWidth = [0.05], TradeEntryLevelOffset = [0, 0.0025, -0.0025], TradeStopLoss = [0.0025, 0.005], TradeTakeProfit = [0.0025, 0.005], MaxProfitTradePerDay = [1,2], MaxLossTradePerDay = [1,2], TradePeriodLength = [90,180,270,360], StopLossTakeProfitRelativeToRange = [1], TimeInStdUnitPerDay = 1440, block_cutting_dimension = "Time Dimension", InitialResultCacheSize = None, TimeFrame = "1 min"):
    
    print("Start of CUDARangeTradeOnSpecificPastTimeRangeStrategy")
    # if GPU_CORE_BLOCK_SIZE <= 16:
    #     GPU_CORE_BLOCK_SIZE_Z = GPU_CORE_BLOCK_SIZE
    #     GPU_CORE_BLOCK_SIZE_X = 1
    #     GPU_CORE_BLOCK_SIZE_Y = 1
    # else:
    #     GPU_CORE_BLOCK_SIZE_Z = 16
    #     GPU_CORE_BLOCK_SIZE_Y = int( GPU_CORE_BLOCK_SIZE / 16)
    #     GPU_CORE_BLOCK_SIZE_X = 1
    # if GPU_CORE_BLOCK_SIZE_Y > 8:
    #     GPU_CORE_BLOCK_SIZE_X = int( GPU_CORE_BLOCK_SIZE_Y / 8)
    #     GPU_CORE_BLOCK_SIZE_Y = 8
        
    GPU_CORE_TOTAL_THREAD_SIZE = Config.CONFIG_CUDA_ThreadCount
    GPU_CORE_BLOCK_SIZE = min(1024,GPU_CORE_TOTAL_THREAD_SIZE)
    GPU_CORE_GRID_SIZE = math.ceil(GPU_CORE_TOTAL_THREAD_SIZE / 1024)
    print('GPU_CORE_TOTAL_THREAD_SIZE is ' + str(GPU_CORE_TOTAL_THREAD_SIZE) + ', GPU_CORE_BLOCK_SIZE is ' + str(GPU_CORE_BLOCK_SIZE) + ', GPU_CORE_GRID_SIZE is' + str(GPU_CORE_GRID_SIZE))

    TRADE_RESULT_COLUMNS = ['long short flag', 'ticker id', 'obs time id', 'obs end time id', 'obs range top price', 'obs range bottom price', 'entry time id', 'entry price', 'exit time id', 'exit price', 'obs start TimeInStandardUnit', 'obs end TimeInStandardUnit', 'start trading TimeInStandardUnit', 'trade period length', 'min range width', 'max range width', 'trade entry level offset', 'stop loss', 'take profit', 'stop loss take profit relative to range', 'max profit trade per day', 'max loss trade per day', 'stop time id', 'obs range top price take profit', 'obs range top price stop loss', 'obs range bottom price take profit', 'obs range bottom price stop loss']
    TRADE_RESULT_COLUMN_COUNT = len(TRADE_RESULT_COLUMNS)
    block_cutting_by_time = 0
    ErrorCode = 0
    ticker_count = len(close_price_matrix)
    DateCount = len(date_id_matrix)
    
    StartTradingTimeList = [StartTimeInStdUnit]
    tempStartTimeInStdUnit = StartTimeInStdUnit
    while tempStartTimeInStdUnit + TimeIntervalInStdUnit <= EndTimeInStdUnit:
        tempStartTimeInStdUnit = tempStartTimeInStdUnit + TimeIntervalInStdUnit
        StartTradingTimeList.append(tempStartTimeInStdUnit)

    BackdateTimePeriodPairList = []
    obs_backdate_start = -MaxBackdateTimePeriodInStdUnit
    while obs_backdate_start < -MinBackdateTimePeriodInStdUnit:
        obs_backdate_end = obs_backdate_start + MinRangeTimeWidthInStdUnit
        while obs_backdate_end < -MinBackdateTimePeriodInStdUnit:
        	    BackdateTimePeriodPairList.append([obs_backdate_start, obs_backdate_end])
        	    obs_backdate_end = obs_backdate_end + RangeBoundaryTimeIntervalInStdUnit
        obs_backdate_start = obs_backdate_start + RangeBoundaryTimeIntervalInStdUnit

    print('BackdateTimePeriodPairList is with length '  + str(len(BackdateTimePeriodPairList)))
    print(str(BackdateTimePeriodPairList))

        
    date_time_matrix = np.vstack((date_id_matrix,time_std_unit_matrix)).T
        
    df_time = pd.DataFrame(data=date_time_matrix, columns=["date id", "time in std unit"]).reset_index().rename(columns={"index":"time id"})
    df_time['date adj time in std unit'] = df_time['date id'] * TimeInStdUnitPerDay + df_time['time in std unit']
    # df_time.to_csv(r'd:\temp\date_time_matrix.csv', index=False)

 
    df = pd.DataFrame(data=StartTradingTimeList, columns=["start trading time in std unit"])
    df['dummy'] = 1
    df2 = pd.DataFrame(data=BackdateTimePeriodPairList, columns=["obs backdate start", "obs backdate end"])
    df2['dummy'] = 1

    df_parameter = df.merge(df2, on='dummy').drop(['dummy'], axis = 1).reset_index().rename(columns={"index":"time parameter set id"})
    df_parameter_out = df_parameter[['start trading time in std unit', 'obs backdate start', 'obs backdate end']]
    # df_parameter.to_csv(r'C:\temp\time_parameter_matrix with missing.csv', index=False)
    
    time_parameter_matrix = df_parameter_out.to_numpy().astype(np.float32).copy(order="C")
    time_parameter_count = len(time_parameter_matrix)
    
    time_parameter_id_list = df_parameter['time parameter set id'].values.tolist()
    

    df_start_trading_time = df_time.merge(df_parameter, left_on='time in std unit', right_on='start trading time in std unit')

    df_start_trading_time['range start time id'] = df_start_trading_time['time id'] + df_start_trading_time['obs backdate start']
    df_start_trading_time = df_start_trading_time.loc[df_start_trading_time['range start time id'] >= 0]
    df_start_trading_time['range start time id'] = df_start_trading_time['range start time id'].astype(int)
    
    df_start_searching_time_id = df_start_trading_time[['time parameter set id', 'time id', 'date adj time in std unit', 'range start time id']]
    df_start_searching_time_id.sort_values('time parameter set id', ascending=True, inplace=True)

    start_searching_time_id_matrix = df_start_searching_time_id.to_numpy().astype(np.float32).copy(order="C")
    start_searching_time_id_count = len(df_start_searching_time_id)
    scenario_column = {'time parameter set index':time_parameter_id_list, 'trade period length':TradePeriodLength, 'min range width':MinRangeWidth, 'max range width':MaxRangeWidth, 'trade entry level offset':TradeEntryLevelOffset, 'stop loss':TradeStopLoss, 'take profit':TradeTakeProfit, 'stop loss take profit relative to range':StopLossTakeProfitRelativeToRange, 'max profit trade per day':MaxProfitTradePerDay, 'max loss trade per day':MaxLossTradePerDay}

    scenario_matrix = InitialiseScenarioMatrix(ticker_count, scenario_column)
    # print("dimension of scenario_matrix is " + str(len(scenario_matrix)) + " x " + str(len(scenario_matrix[0])))
    # print(scenario_matrix)
    scenario_count = len(scenario_matrix)
    scenario_column_count = len(scenario_matrix[0])
    print('scenario_count is ' + str(scenario_count))
    
    
    df = pd.DataFrame(data=scenario_matrix, columns=['id', 'time parameter set index', 'trade period length', 'min range width', 'max range width', 'trade entry level offset', 'stop loss', 'take profit', 'stop loss take profit relative to range', 'max profit trade per day', 'max loss trade per day'])
    df['scenario id'] = df.index

    if block_cutting_dimension == "Time Dimension":
        close_price_matrix = close_price_matrix.T.copy(order="C")
        high_price_matrix = high_price_matrix.T.copy(order="C")
        low_price_matrix = low_price_matrix.T.copy(order="C")
        date_id_matrix = date_id_matrix.T.copy(order="C")
        time_std_unit_matrix = time_std_unit_matrix.T.copy(order="C")
        block_cutting_by_time = 1

    if InitialResultCacheSize is None or InitialResultCacheSize == 0:
        InitialResultCacheSize = 30000000

    print("InitialResultCacheSize is " + f"{InitialResultCacheSize:,}")
    

    first_dimension_size = len(close_price_matrix)
    second_dimension_size = len(close_price_matrix[0])

    # gpu_core_block_count = math.ceil(scenario_count/GPU_CORE_BLOCK_SIZE)
    gpu_core_block_count = math.ceil(scenario_count/(GPU_CORE_BLOCK_SIZE * GPU_CORE_GRID_SIZE))
    
    print("gpu_core_block_count is " + str(gpu_core_block_count))

    trade_result_count = np.int32(0)
    
    trade_result = np.zeros((InitialResultCacheSize, TRADE_RESULT_COLUMN_COUNT)).astype(np.float32) #long short flag, ticker id, obs time id, entry time id, entry price, exit time id, exit price, trade id
    
    close_price_matrix = close_price_matrix.astype(np.float32)
    high_price_matrix = high_price_matrix.astype(np.float32)
    low_price_matrix = low_price_matrix.astype(np.float32)
    date_id_matrix = date_id_matrix.astype(np.float32)
    time_std_unit_matrix = time_std_unit_matrix.astype(np.float32)
    
    close_price_matrix_gpu = cuda.mem_alloc(close_price_matrix.nbytes)
    high_price_matrix_gpu = cuda.mem_alloc(high_price_matrix.nbytes)
    low_price_matrix_gpu = cuda.mem_alloc(low_price_matrix.nbytes)
    date_id_matrix_gpu = cuda.mem_alloc(date_id_matrix.nbytes)
    trade_result_count_gpu = cuda.mem_alloc(trade_result_count.nbytes)
    time_std_unit_matrix_gpu = cuda.mem_alloc(time_std_unit_matrix.nbytes)
    trade_result_gpu = cuda.mem_alloc(trade_result.nbytes)
    scenario_matrix_gpu = cuda.mem_alloc(scenario_matrix.nbytes)
    time_parameter_matrix_gpu = cuda.mem_alloc(time_parameter_matrix.nbytes)
    start_searching_time_id_matrix_gpu = cuda.mem_alloc(start_searching_time_id_matrix.nbytes)
    
    cuda.memcpy_htod(close_price_matrix_gpu, close_price_matrix)
    cuda.memcpy_htod(high_price_matrix_gpu, high_price_matrix)
    cuda.memcpy_htod(low_price_matrix_gpu, low_price_matrix)
    cuda.memcpy_htod(date_id_matrix_gpu, date_id_matrix)
    cuda.memcpy_htod(trade_result_count_gpu, trade_result_count)
    cuda.memcpy_htod(time_std_unit_matrix_gpu, time_std_unit_matrix)
    cuda.memcpy_htod(trade_result_gpu, trade_result)
    cuda.memcpy_htod(scenario_matrix_gpu, scenario_matrix)
    cuda.memcpy_htod(time_parameter_matrix_gpu, time_parameter_matrix)
    cuda.memcpy_htod(start_searching_time_id_matrix_gpu, start_searching_time_id_matrix)

    AdditionalResultCount = np.zeros(1, dtype=np.int32)
    AdditionalResultCount_gpu = cuda.mem_alloc(AdditionalResultCount.nbytes)
    cuda.memcpy_htod(AdditionalResultCount_gpu, AdditionalResultCount)

    mod = SourceModule("""
      #include <cstdlib>

      __device__ int add_trade(unsigned long long *AdditionalResultCount, int *trade_result_count, int TRADE_RESULT_COLUMN_COUNT, float *trade_result, int long_short_flag, int ticker_id, int obs_start_time_id, int obs_end_time_id, float obs_range_top_price, float obs_range_bottom_price, int entry_time_id, float entry_price, int exit_time_id, float exit_price, int obs_start_time, int obs_end_time, int start_trading_time, int trade_period_length, float min_range_width, float max_range_width, float trade_entry_level_offset, float stop_loss, float take_profit, int stop_loss_take_profit_relative_to_range, int max_profit_trade_per_day, int max_loss_trade_per_day, int stop_time_id, float obs_range_top_price_take_profit, float obs_range_top_price_stop_loss, float obs_range_bottom_price_take_profit, float obs_range_bottom_price_stop_loss)
        {

        int trade_result_index, trade_result_index_offset, temp_AdditionalResultCount;

//    TRADE_RESULT_COLUMNS = ['long short flag', 'ticker id', 'obs time id', 'obs end time id', 'obs range top price', 'obs range bottom price', 'entry time id', 'entry price', 'exit time id', 'exit price', 'obs start TimeInStandardUnit', 'obs end TimeInStandardUnit', 'start trading TimeInStandardUnit', 'trade period length', 'min range width', 'max range width', 'trade entry level offset', 'stop loss', 'take profit', 'stop loss take profit relative to range', 'max profit trade per day', 'max loss trade per day', 'stop time id']

                        trade_result_index = atomicAdd(trade_result_count,1);
                        trade_result_index_offset = trade_result_index * TRADE_RESULT_COLUMN_COUNT ;
                        trade_result[trade_result_index_offset + 0] = (float) long_short_flag;
                        trade_result[trade_result_index_offset + 1] = ticker_id;
                        trade_result[trade_result_index_offset + 2] = obs_start_time_id;
                        trade_result[trade_result_index_offset + 3] = obs_end_time_id;
                        trade_result[trade_result_index_offset + 4] = obs_range_top_price;
                        trade_result[trade_result_index_offset + 5] = obs_range_bottom_price;
                        trade_result[trade_result_index_offset + 6] = entry_time_id;
                        trade_result[trade_result_index_offset + 7] = entry_price;
                        trade_result[trade_result_index_offset + 8] = exit_time_id;
                        trade_result[trade_result_index_offset + 9] = exit_price;
                        trade_result[trade_result_index_offset + 10] = obs_start_time;
                        trade_result[trade_result_index_offset + 11] = obs_end_time;
                        trade_result[trade_result_index_offset + 12] = start_trading_time;
                        trade_result[trade_result_index_offset + 13] = trade_period_length;
                        trade_result[trade_result_index_offset + 14] = min_range_width;
                        trade_result[trade_result_index_offset + 15] = max_range_width;
                        trade_result[trade_result_index_offset + 16] = trade_entry_level_offset;
                        trade_result[trade_result_index_offset + 17] = stop_loss;
                        trade_result[trade_result_index_offset + 18] = take_profit;
                        trade_result[trade_result_index_offset + 19] = stop_loss_take_profit_relative_to_range;
                        trade_result[trade_result_index_offset + 20] = max_profit_trade_per_day;
                        trade_result[trade_result_index_offset + 21] = max_loss_trade_per_day;
                        trade_result[trade_result_index_offset + 22] = stop_time_id;
                        
                        trade_result[trade_result_index_offset + 23] = obs_range_top_price_take_profit;
                        trade_result[trade_result_index_offset + 24] = obs_range_top_price_stop_loss;
                        trade_result[trade_result_index_offset + 25] = obs_range_bottom_price_take_profit;
                        trade_result[trade_result_index_offset + 26] = obs_range_bottom_price_stop_loss;

                        temp_AdditionalResultCount = atomicAdd(AdditionalResultCount,1);
                       
                    return 0;
      }

      __device__ int try_enter_position( float *entry_price_returned, int *profit_trade_count, int *loss_trade_count, float price_before, float price_after, float range_top_stop_loss_price, float range_bottom_stop_loss_price, unsigned long long *AdditionalResultCount, int *trade_result_count, int TRADE_RESULT_COLUMN_COUNT, float *trade_result, int ticker_id, int obs_start_time_id, int obs_end_time_id, float obs_range_top_price, float obs_range_bottom_price, int time_id, int obs_start_time, int obs_end_time, int start_trading_time, int trade_period_length, float min_range_width, float max_range_width, float trade_entry_level_offset, float stop_loss, float take_profit, int stop_loss_take_profit_relative_to_range, int max_profit_trade_per_day, int max_loss_trade_per_day, int stop_time_id, float obs_range_top_price_take_profit, float obs_range_top_price_stop_loss, float obs_range_bottom_price_take_profit, float obs_range_bottom_price_stop_loss)
        {
          if (price_before <= obs_range_top_price && price_before >= obs_range_bottom_price && profit_trade_count[0] < max_profit_trade_per_day && loss_trade_count[0] < max_loss_trade_per_day) {
            if (price_after > range_top_stop_loss_price) {
              add_trade( AdditionalResultCount, trade_result_count, TRADE_RESULT_COLUMN_COUNT, trade_result, -1, ticker_id, obs_start_time_id, obs_end_time_id, obs_range_top_price, obs_range_bottom_price, time_id, obs_range_top_price, time_id, range_top_stop_loss_price, obs_start_time, obs_end_time, start_trading_time, trade_period_length, min_range_width, max_range_width, trade_entry_level_offset, stop_loss, take_profit, stop_loss_take_profit_relative_to_range, max_profit_trade_per_day, max_loss_trade_per_day, time_id, obs_range_top_price_take_profit, obs_range_top_price_stop_loss, obs_range_bottom_price_take_profit, obs_range_bottom_price_stop_loss);
              loss_trade_count[0]++;
              return 0;
            } else if (price_after < range_bottom_stop_loss_price) {
              add_trade( AdditionalResultCount, trade_result_count, TRADE_RESULT_COLUMN_COUNT, trade_result, 1, ticker_id, obs_start_time_id, obs_end_time_id, obs_range_top_price, obs_range_bottom_price, time_id, obs_range_bottom_price, time_id, range_bottom_stop_loss_price, obs_start_time, obs_end_time, start_trading_time, trade_period_length, min_range_width, max_range_width, trade_entry_level_offset, stop_loss, take_profit, stop_loss_take_profit_relative_to_range, max_profit_trade_per_day, max_loss_trade_per_day, time_id, obs_range_top_price_take_profit, obs_range_top_price_stop_loss, obs_range_bottom_price_take_profit, obs_range_bottom_price_stop_loss);
              loss_trade_count[0]++;
              return 0;
            } else if (price_after > obs_range_top_price) {
              entry_price_returned[0] = obs_range_top_price;
              return -1;
            } else if (price_after < obs_range_bottom_price) {
              entry_price_returned[0] = obs_range_bottom_price;
              return 1;
            }
          } 
          return 0;
        }

        __device__ int try_close_position( float price_after, int *profit_trade_count, int *loss_trade_count, float stop_loss_price, float take_profit_price, unsigned long long *AdditionalResultCount, int *trade_result_count, int TRADE_RESULT_COLUMN_COUNT, float *trade_result, int long_short_flag, int ticker_id, int obs_start_time_id, int obs_end_time_id, float obs_range_top_price, float obs_range_bottom_price, int entry_time_id, float entry_price, int exit_time_id, int obs_start_time, int obs_end_time, int start_trading_time, int trade_period_length, float min_range_width, float max_range_width, float trade_entry_level_offset, float stop_loss, float take_profit, int stop_loss_take_profit_relative_to_range, int max_profit_trade_per_day, int max_loss_trade_per_day, float obs_range_top_price_take_profit, float obs_range_top_price_stop_loss, float obs_range_bottom_price_take_profit, float obs_range_bottom_price_stop_loss)
        {
          if (long_short_flag < 0) {
            if (price_after > stop_loss_price) {
              loss_trade_count[0]++;
              add_trade( AdditionalResultCount, trade_result_count, TRADE_RESULT_COLUMN_COUNT, trade_result, long_short_flag, ticker_id, obs_start_time_id, obs_end_time_id, obs_range_top_price, obs_range_bottom_price, entry_time_id, entry_price, exit_time_id, stop_loss_price, obs_start_time, obs_end_time, start_trading_time, trade_period_length, min_range_width, max_range_width, trade_entry_level_offset, stop_loss, take_profit, stop_loss_take_profit_relative_to_range, max_profit_trade_per_day, max_loss_trade_per_day, exit_time_id, obs_range_top_price_take_profit, obs_range_top_price_stop_loss, obs_range_bottom_price_take_profit, obs_range_bottom_price_stop_loss);
              return 0;
            } else if (price_after < take_profit_price) {
              profit_trade_count[0]++;
              add_trade( AdditionalResultCount, trade_result_count, TRADE_RESULT_COLUMN_COUNT, trade_result, long_short_flag, ticker_id, obs_start_time_id, obs_end_time_id, obs_range_top_price, obs_range_bottom_price, entry_time_id, entry_price, exit_time_id, take_profit_price, obs_start_time, obs_end_time, start_trading_time, trade_period_length, min_range_width, max_range_width, trade_entry_level_offset, stop_loss, take_profit, stop_loss_take_profit_relative_to_range, max_profit_trade_per_day, max_loss_trade_per_day, exit_time_id, obs_range_top_price_take_profit, obs_range_top_price_stop_loss, obs_range_bottom_price_take_profit, obs_range_bottom_price_stop_loss);
              return 0;
            } else {
              return long_short_flag;
            }
          } else if (long_short_flag > 0) {
            if (price_after < stop_loss_price) {
              loss_trade_count[0]++;
              add_trade( AdditionalResultCount, trade_result_count, TRADE_RESULT_COLUMN_COUNT, trade_result, long_short_flag, ticker_id, obs_start_time_id, obs_end_time_id, obs_range_top_price, obs_range_bottom_price, entry_time_id, entry_price, exit_time_id, stop_loss_price, obs_start_time, obs_end_time, start_trading_time, trade_period_length, min_range_width, max_range_width, trade_entry_level_offset, stop_loss, take_profit, stop_loss_take_profit_relative_to_range, max_profit_trade_per_day, max_loss_trade_per_day, exit_time_id, obs_range_top_price_take_profit, obs_range_top_price_stop_loss, obs_range_bottom_price_take_profit, obs_range_bottom_price_stop_loss);
              return 0;
            } else if (price_after > take_profit_price) {
              profit_trade_count[0]++;
              add_trade( AdditionalResultCount, trade_result_count, TRADE_RESULT_COLUMN_COUNT, trade_result, long_short_flag, ticker_id, obs_start_time_id, obs_end_time_id, obs_range_top_price, obs_range_bottom_price, entry_time_id, entry_price, exit_time_id, take_profit_price, obs_start_time, obs_end_time, start_trading_time, trade_period_length, min_range_width, max_range_width, trade_entry_level_offset, stop_loss, take_profit, stop_loss_take_profit_relative_to_range, max_profit_trade_per_day, max_loss_trade_per_day, exit_time_id, obs_range_top_price_take_profit, obs_range_top_price_stop_loss, obs_range_bottom_price_take_profit, obs_range_bottom_price_stop_loss);
              return 0;
            } else {
              return long_short_flag;
            }
          }
          return long_short_flag;
        }
            
      __device__ int get_date_adjusted_time( int time_id, int TimeInStdUnitPerDay, float *date_id_data, float *time_std_unit_data)
        {
          return date_id_data[time_id] * TimeInStdUnitPerDay + time_std_unit_data[time_id];
        }

      __global__ void range_trade_on_specific_past_time_range_analysis(int block_cutting_by_time, int second_dimension_size, int gpu_core_block_count, int first_dimension_size, int scenario_count, int scenario_column_count, int time_parameter_count, int start_searching_time_id_count, int TimeIntervalInStdUnit, int TimeInStdUnitPerDay, int MaxBackdateTimePeriodInStdUnit, int MinBackdateTimePeriodInStdUnit, int ErrorCode, int TRADE_RESULT_COLUMN_COUNT, unsigned long long *AdditionalResultCount, int *trade_result_count, float *close_data, float *high_data, float *low_data, float *date_id_data, float *time_std_unit_data, float *scenario_matrix, float *time_parameter_matrix, float *start_searching_time_id_matrix, float *trade_result)
      {
        int thread_Index, GPU_CORE_BLOCK_SIZE, temp, scenario_id, scenario_id_offset, ticker_id, time_parameter_id, start_trading_time, start_trading_time2, start_trading_time_date_adj_time2, start_searching_time_id2, obs_backdate_start, obs_backdate_end, trade_period_length, stop_loss_take_profit_relative_to_range, max_profit_trade_per_day, max_loss_trade_per_day, day_adjusted_time, obs_backdate_start_boundary, obs_backdate_end_boundary, obs_backdate_start_time_id, obs_backdate_end_time_id, end_trading_time_id, profit_trade_count[1], loss_trade_count[1], range_section, long_short_flag, start_trading_time_id, time_parameter_id2, entry_time_id; 
        float min_range_width, max_range_width, trade_entry_level_offset, stop_loss, take_profit, temp_stop_loss, temp_take_profit, range_price_high, range_price_low, range_width, range_top_stop_loss_price, range_top_take_profit_price, range_bottom_stop_loss_price, range_bottom_take_profit_price, entry_price, exit_price, prior_price, current_price, price_pairs[4], entry_price_returned[1];
        
        GPU_CORE_BLOCK_SIZE = blockDim.x * gridDim.x;
        thread_Index = blockIdx.x * blockDim.x + threadIdx.x;
//          GPU_CORE_BLOCK_SIZE = GPU_CORE_BLOCK_SIZE_X * GPU_CORE_BLOCK_SIZE_Y * GPU_CORE_BLOCK_SIZE_Z;
 //         thread_Index = threadIdx.x * GPU_CORE_BLOCK_SIZE_Y * GPU_CORE_BLOCK_SIZE_Z + threadIdx.y * GPU_CORE_BLOCK_SIZE_Z + threadIdx.z;

//          add_trade( AdditionalResultCount, trade_result_count, TRADE_RESULT_COLUMN_COUNT, trade_result, thread_Index, -100, GPU_CORE_BLOCK_SIZE, GPU_CORE_BLOCK_SIZE_X, GPU_CORE_BLOCK_SIZE_Y, GPU_CORE_BLOCK_SIZE_Z, gpu_core_block_count, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);

          for (int k = 0; k < gpu_core_block_count; k++) {

//                              add_trade( AdditionalResultCount, trade_result_count, TRADE_RESULT_COLUMN_COUNT, trade_result, 0, k, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);

            scenario_id = k * GPU_CORE_BLOCK_SIZE + thread_Index;
            if (scenario_id < scenario_count) {

                    
              scenario_id_offset = scenario_id * scenario_column_count;
              ticker_id = (int) scenario_matrix[scenario_id_offset];
//    scenario_column = {'start trading TimeInStandardUnit':StartTradingTimeList, 'trade period length':TradePeriodLength, 'min range width':MinRangeWidth, 'max range width':MaxRangeWidth, 'trade entry level offset':TradeEntryLevelOffset, 'stop loss':TradeStopLoss, 'take profit':TradeTakeProfit, 'stop loss take profit relative to range':[0, 1], 'max profit trade per day':MaxProfitTradePerDay, 'max loss trade per day':MaxLossTradePerDay}
              time_parameter_id = (int) scenario_matrix[scenario_id_offset + 1];
              
              start_trading_time = (int) time_parameter_matrix[time_parameter_id * 3];
              obs_backdate_start = (int) time_parameter_matrix[time_parameter_id * 3 + 1];
              obs_backdate_end = (int) time_parameter_matrix[time_parameter_id * 3 + 2];
              
//              if (k == 0) {
//                 add_trade( AdditionalResultCount, trade_result_count, TRADE_RESULT_COLUMN_COUNT, trade_result, scenario_id, -90, 0, 0, 0, 0, 0, 0, 0, 0, obs_backdate_start, obs_backdate_end, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);
//              }
              
              trade_period_length = (int) scenario_matrix[scenario_id_offset + 2];
              min_range_width = scenario_matrix[scenario_id_offset + 3];
              max_range_width = scenario_matrix[scenario_id_offset + 4];
              trade_entry_level_offset = scenario_matrix[scenario_id_offset + 5];
              stop_loss = scenario_matrix[scenario_id_offset + 6];
              take_profit = scenario_matrix[scenario_id_offset + 7];
              stop_loss_take_profit_relative_to_range = scenario_matrix[scenario_id_offset + 8];
              max_profit_trade_per_day = scenario_matrix[scenario_id_offset + 9];
              max_loss_trade_per_day = scenario_matrix[scenario_id_offset + 10];

              for (int i=0; i<start_searching_time_id_count; i++) {

                time_parameter_id2 = (int) start_searching_time_id_matrix[i * 4];

                if (time_parameter_id2 == time_parameter_id) {

                  start_trading_time_id = (int) start_searching_time_id_matrix[i * 4 + 1];
                  start_trading_time_date_adj_time2 = (int) start_searching_time_id_matrix[i * 4 + 2];
                  obs_backdate_start_time_id = (int) start_searching_time_id_matrix[i * 4 + 3];

                  for (int time_id = obs_backdate_start_time_id; time_id < start_trading_time_id - 1; time_id++) {
                    day_adjusted_time = get_date_adjusted_time( time_id, TimeInStdUnitPerDay, date_id_data, time_std_unit_data);
                    if (day_adjusted_time > start_trading_time_date_adj_time2 + obs_backdate_start) {
                      obs_backdate_start_time_id = time_id;
                      break;
                    }
                  }                        

                  obs_backdate_end_time_id = start_trading_time_id - 1;
                  
                  for (int time_id = obs_backdate_start_time_id; time_id < start_trading_time_id - 1; time_id++) {
                    day_adjusted_time = get_date_adjusted_time( time_id, TimeInStdUnitPerDay, date_id_data, time_std_unit_data);
                    if (day_adjusted_time > start_trading_time_date_adj_time2 + obs_backdate_end) {
                      obs_backdate_end_time_id = time_id;
                      break;
                    }
                  }

                  range_price_high = high_data[obs_backdate_start_time_id];
                  range_price_low = low_data[obs_backdate_start_time_id];
                  for (int obs_time_id = obs_backdate_start_time_id + 1; obs_time_id <= obs_backdate_end_time_id; obs_time_id++) {
                    if (high_data[obs_time_id] > range_price_high) {
                      range_price_high = high_data[obs_time_id];
                    }
                    if (low_data[obs_time_id] < range_price_low) {
                      range_price_low = low_data[obs_time_id];
                    }
                  }
                        
                  if (stop_loss_take_profit_relative_to_range == 0) {
                    range_price_high = range_price_high * (1 + trade_entry_level_offset);
                    range_price_low = range_price_low * (1 - trade_entry_level_offset);
                  } else {
                    range_width = range_price_high - range_price_low;
                    range_price_high = range_price_high + (trade_entry_level_offset * range_width);
                    range_price_low = range_price_low - (trade_entry_level_offset * range_width);
                  }
                  range_width = (range_price_high - range_price_low) / range_price_low;

                  if (range_width > min_range_width && range_width < max_range_width) {


                    if (stop_loss_take_profit_relative_to_range == 0) {
                      range_top_stop_loss_price = range_price_high * (1 + stop_loss);
                      range_top_take_profit_price = range_price_high * (1 - take_profit);
                      range_bottom_stop_loss_price = range_price_low * (1 - stop_loss);
                      range_bottom_take_profit_price = range_price_low * (1 + take_profit);
                    } else {
                      range_top_stop_loss_price = range_price_high + (range_width * range_price_low * stop_loss);
                      range_top_take_profit_price = range_price_high - (range_width * range_price_low * take_profit);
                      range_bottom_stop_loss_price = range_price_low - (range_width * range_price_low * stop_loss);
                      range_bottom_take_profit_price = range_price_low + (range_width * range_price_low * take_profit);
                    }
                    profit_trade_count[0] = 0;
                    loss_trade_count[0] = 0;
                    range_section = 0;
                    long_short_flag = 0;
                    
//                              add_trade( AdditionalResultCount, trade_result_count, TRADE_RESULT_COLUMN_COUNT, trade_result, 0, -40, obs_backdate_start_time_id, obs_backdate_end_time_id, range_price_high, range_price_low, 0, 0, 0, 0, obs_backdate_start, obs_backdate_end, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, range_top_take_profit_price, range_top_stop_loss_price, range_bottom_take_profit_price, range_bottom_stop_loss_price);


                    for (int trade_time_id = start_trading_time_id + 1; trade_time_id <= start_trading_time_id + trade_period_length; trade_time_id++) {
                      if (profit_trade_count[0] >= max_profit_trade_per_day || loss_trade_count[0] >= max_loss_trade_per_day) {
                        break;
                      }
                      price_pairs[0] = close_data[trade_time_id - 1];
                      if (prior_price < close_data[trade_time_id]) {
                        price_pairs[1] = low_data[trade_time_id];
                        price_pairs[2] = high_data[trade_time_id];
                      } else {
                        price_pairs[1] = high_data[trade_time_id];
                        price_pairs[2] = low_data[trade_time_id];
                      }
                      price_pairs[3] = close_data[trade_time_id];

                      for (int price_index = 0; price_index < 3; price_index++) {
                        if (long_short_flag == 0) {
                          long_short_flag = try_enter_position(entry_price_returned, profit_trade_count, loss_trade_count, price_pairs[price_index], price_pairs[price_index + 1], range_top_stop_loss_price, range_bottom_stop_loss_price, AdditionalResultCount, trade_result_count, TRADE_RESULT_COLUMN_COUNT, trade_result, ticker_id, obs_backdate_start_time_id, obs_backdate_end_time_id, range_price_high, range_price_low, trade_time_id, obs_backdate_start, obs_backdate_end, start_trading_time, trade_period_length, min_range_width, max_range_width, trade_entry_level_offset, stop_loss, take_profit, stop_loss_take_profit_relative_to_range, max_profit_trade_per_day, max_loss_trade_per_day, trade_time_id, range_top_take_profit_price, range_top_stop_loss_price, range_bottom_take_profit_price, range_bottom_stop_loss_price);
                          if (long_short_flag != 0) {
                            entry_time_id = trade_time_id;
                          }
                        } else {
                          if (long_short_flag < 0) {
                            temp_stop_loss = range_top_stop_loss_price;
                            temp_take_profit = range_top_take_profit_price;
                          } else {
                            temp_stop_loss = range_bottom_stop_loss_price;
                            temp_take_profit = range_bottom_take_profit_price;
                          }
                          long_short_flag = try_close_position(price_pairs[price_index + 1], profit_trade_count, loss_trade_count, temp_stop_loss, temp_take_profit, AdditionalResultCount, trade_result_count, TRADE_RESULT_COLUMN_COUNT, trade_result, long_short_flag, ticker_id, obs_backdate_start_time_id, obs_backdate_end_time_id, range_price_high, range_price_low, entry_time_id, entry_price_returned[0], trade_time_id, obs_backdate_start, obs_backdate_end, start_trading_time, trade_period_length, min_range_width, max_range_width, trade_entry_level_offset, stop_loss, take_profit, stop_loss_take_profit_relative_to_range, max_profit_trade_per_day, max_loss_trade_per_day, range_top_take_profit_price, range_top_stop_loss_price, range_bottom_take_profit_price, range_bottom_stop_loss_price);
                          if (long_short_flag == 0) {
                            entry_time_id = 0;
                            entry_price_returned[0] = 0.0;
                          }
                        }
                      }
                          }
                    if (long_short_flag != 0) {
                      add_trade( AdditionalResultCount, trade_result_count, TRADE_RESULT_COLUMN_COUNT, trade_result, long_short_flag, ticker_id, obs_backdate_start_time_id, obs_backdate_end_time_id, range_price_high, range_price_low, entry_time_id, entry_price_returned[0], start_trading_time_id + trade_period_length, close_data[start_trading_time_id + trade_period_length], obs_backdate_start, obs_backdate_end, start_trading_time, trade_period_length, min_range_width, max_range_width, trade_entry_level_offset, stop_loss, take_profit, stop_loss_take_profit_relative_to_range, max_profit_trade_per_day, max_loss_trade_per_day, start_trading_time_id + trade_period_length, range_top_take_profit_price, range_top_stop_loss_price, range_bottom_take_profit_price, range_bottom_stop_loss_price);
                    }
                  }
                } else if (time_parameter_id2 > time_parameter_id) {
                  break;
                }              
              }
            }
          }     
      }
      """)

    func = mod.get_function("range_trade_on_specific_past_time_range_analysis")
    func(np.int32(block_cutting_by_time), np.int32(second_dimension_size), np.int32(gpu_core_block_count), np.int32(first_dimension_size), np.int32(scenario_count), np.int32(scenario_column_count), np.int32(time_parameter_count), np.int32(start_searching_time_id_count), np.int32(TimeIntervalInStdUnit), np.int32(TimeInStdUnitPerDay), np.int32(MaxBackdateTimePeriodInStdUnit), np.int32(MinBackdateTimePeriodInStdUnit),  np.int32(ErrorCode), np.int32(TRADE_RESULT_COLUMN_COUNT), AdditionalResultCount_gpu, trade_result_count_gpu, close_price_matrix_gpu, high_price_matrix_gpu, low_price_matrix_gpu, date_id_matrix_gpu, time_std_unit_matrix_gpu, scenario_matrix_gpu, time_parameter_matrix_gpu, start_searching_time_id_matrix_gpu, trade_result_gpu, block=(GPU_CORE_BLOCK_SIZE,1,1), grid=(GPU_CORE_GRID_SIZE, 1))

    AdditionalResultCount_out = np.empty_like(AdditionalResultCount)
    cuda.memcpy_dtoh(AdditionalResultCount_out, AdditionalResultCount_gpu)

    print("AdditionalResultCount_out[0] is " + f"{AdditionalResultCount_out[0]:,}")
    print()
    
    if (AdditionalResultCount_out[0] > InitialResultCacheSize - 2):
        print()
        print('InitialResultCacheSize not large enough')
        print()
        raise Exception('InitialResultCacheSize not large enough')
        
        
    trade_result_count_out = np.empty_like(trade_result_count)
    cuda.memcpy_dtoh(trade_result_count_out, trade_result_count_gpu)
    trade_record = np.empty_like(trade_result)
    cuda.memcpy_dtoh(trade_record, trade_result_gpu)
    
    trade_result_gpu.free()
    close_price_matrix_gpu.free()
    high_price_matrix_gpu.free()
    low_price_matrix_gpu.free()
    date_id_matrix_gpu.free()
    scenario_matrix_gpu.free()
    trade_result_count_gpu.free()
    time_std_unit_matrix_gpu.free()
    
    return pd.DataFrame(data=trade_record[0:trade_result_count_out], columns=TRADE_RESULT_COLUMNS)

    # df = pd.DataFrame(data=trade_record[0:trade_result_count_out], columns=TRADE_RESULT_COLUMNS)
    # df.sort_values(['obs time id', 'obs end time id', 'entry time id'], ascending=[True, True, True], inplace=True)

    # print('trade record is')
    # print(df)
    # df.to_csv(r'd:\temp\trade_result.csv', index=False)
    
    # df_selected = df[df['ticker id'] < 0]
    # df_selected.to_csv(r'C:\temp\trade_result_debug.csv', index=False)
    
    # print('result is')
    # print(str(trade_record[0]))
    # print(str(trade_record[1]))
    # print(str(trade_record[2]))
    
    # return df

