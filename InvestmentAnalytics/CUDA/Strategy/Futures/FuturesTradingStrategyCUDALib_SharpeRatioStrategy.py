# -*- coding: utf-8 -*-
"""
Created on Fri Oct  8 16:14:22 2021

@author: Henry Cheung
"""


from datetime import date, datetime, timedelta
import pycuda.driver as cuda
import pycuda.autoinit
from pycuda.compiler import SourceModule
import math
import pandas as pd

import InvestmentAnalytics.Config as Config


import InvestmentAnalytics.CUDA.CUDAPathSetting
import numpy as np

# GPU_CORE_BLOCK_SIZE = 32*32
# InitialResultCacheSize = 50000000

# import operator as op
# from functools import reduce 

def AppendListToDF(original_df, column_name, lst):
    if isinstance(lst[0], list):
        col_name_list = []
        for i in range(len(lst[0])):
            col_name_list.append(column_name+' '+str(i))
    else:
        col_name_list = [column_name]
    df = pd.DataFrame(lst, columns =col_name_list)
    # print('df for AppendListToDF for ' + column_name + ' is')
    # print(df)
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


    # scenario_df = AppendListToDF(scenario_df, ObsPeriod, 'obs period')
    # scenario_df = AppendListToDF(scenario_df, SharpeRatioThreshold, 'sharpe ratio threshold')
    # scenario_df = AppendListToDF(scenario_df, ExitSharpeRatioOffset, 'exit sharpe ratio offset')
    # scenario_df = AppendListToDF(scenario_df, StopLossPerTrade, 'stop loss')
    # scenario_df = AppendListToDF(scenario_df, TakeProfitPerTrade, 'take profit')
    # scenario_df = AppendListToDF(scenario_df, MaxHoldingPeriod, 'max holding period')
    scenario_df.drop(columns=['Dummy'], inplace=True)
    # scenario_count = len(scenario_df)

    scenario_matrix = scenario_df.to_numpy().astype(np.float32)
    return scenario_matrix.copy(order="C")
    

def CUDASharpeRatioStrategy(close_price_matrix, volume_matrix, date_id_matrix, time_std_unit_matrix, time_std_unit_to_market_time_section_id_matrix, mean_vol_by_market_time_section_id_matrix, StopLossPerTrade = [0, 0.0025, 0.005], TakeProfitPerTrade = [0, 0.0025, 0.005], MaxHoldingPeriod = [10], VolumeToMeanVolumeRatio = [3], MinReturnPerTimeSlotThreshold = [0.0001], ObsPeriod = [5, 10], SharpeRatioThreshold = [0.5, 1, 2], ExitSharpeRatioOffset = [0, 0.5], time_in_std_unit_per_day = 24*60, TradeFilterIndicatorName = None, TradeFilterIndicatorDataLabel = None, TradeFilterIndicatorParameterList = None, TradeFilterIndicatorThreshold = None, TradeFilterIndicator_matrix_list = None, block_cutting_dimension = "Time Dimension", InitialResultCacheSize = 50000000):
    if TradeFilterIndicatorName is None:
        df_all = CUDASharpeRatioStrategyPerFilterIndicator(close_price_matrix, volume_matrix, date_id_matrix, time_std_unit_matrix, time_std_unit_to_market_time_section_id_matrix, mean_vol_by_market_time_section_id_matrix, StopLossPerTrade = StopLossPerTrade, TakeProfitPerTrade = TakeProfitPerTrade, MaxHoldingPeriod = MaxHoldingPeriod, VolumeToMeanVolumeRatio = VolumeToMeanVolumeRatio, MinReturnPerTimeSlotThreshold = MinReturnPerTimeSlotThreshold, ObsPeriod = ObsPeriod, SharpeRatioThreshold = SharpeRatioThreshold, ExitSharpeRatioOffset = ExitSharpeRatioOffset, time_in_std_unit_per_day = time_in_std_unit_per_day, TradeFilterIndicatorName = TradeFilterIndicatorName, TradeFilterIndicatorDataLabel = TradeFilterIndicatorDataLabel, TradeFilterIndicatorParameter = None, TradeFilterIndicatorThreshold = TradeFilterIndicatorThreshold, TradeFilterIndicator_matrix = None, block_cutting_dimension = block_cutting_dimension, InitialResultCacheSize = InitialResultCacheSize)
    else:
        df_all = pd.DataFrame()
        for i in range(len(TradeFilterIndicatorParameterList)):
            df = CUDASharpeRatioStrategyPerFilterIndicator(close_price_matrix, volume_matrix, date_id_matrix, time_std_unit_matrix, time_std_unit_to_market_time_section_id_matrix, mean_vol_by_market_time_section_id_matrix, StopLossPerTrade = StopLossPerTrade, TakeProfitPerTrade = TakeProfitPerTrade, MaxHoldingPeriod = MaxHoldingPeriod, VolumeToMeanVolumeRatio = VolumeToMeanVolumeRatio, MinReturnPerTimeSlotThreshold = MinReturnPerTimeSlotThreshold, ObsPeriod = ObsPeriod, SharpeRatioThreshold = SharpeRatioThreshold, ExitSharpeRatioOffset = ExitSharpeRatioOffset, time_in_std_unit_per_day = time_in_std_unit_per_day, TradeFilterIndicatorName = TradeFilterIndicatorName, TradeFilterIndicatorDataLabel = TradeFilterIndicatorDataLabel, TradeFilterIndicatorParameter = TradeFilterIndicatorParameterList[i], TradeFilterIndicatorThreshold = TradeFilterIndicatorThreshold, TradeFilterIndicator_matrix = TradeFilterIndicator_matrix_list[i], block_cutting_dimension = block_cutting_dimension, InitialResultCacheSize = InitialResultCacheSize)
            df_all = df_all.append(df)
            
    return df_all

    
    
def CUDASharpeRatioStrategyPerFilterIndicator(close_price_matrix, volume_matrix, date_id_matrix, time_std_unit_matrix, time_std_unit_to_market_time_section_id_matrix, mean_vol_by_market_time_section_id_matrix, StopLossPerTrade = [0, 0.0025, 0.005], TakeProfitPerTrade = [0, 0.0025, 0.005], MaxHoldingPeriod = [10], VolumeToMeanVolumeRatio = [3], MinReturnPerTimeSlotThreshold = [0.0001], ObsPeriod = [5, 10], SharpeRatioThreshold = [0.5, 1, 2], ExitSharpeRatioOffset = [0, 0.5], time_in_std_unit_per_day = 24*60, TradeFilterIndicatorName = None, TradeFilterIndicatorDataLabel = None, TradeFilterIndicatorParameter = None, TradeFilterIndicatorThreshold = None, TradeFilterIndicator_matrix = None, block_cutting_dimension = "Time Dimension", InitialResultCacheSize = 50000000):

    # GPU_CORE_TOTAL_THREAD_SIZE = 1
    # GPU_CORE_TOTAL_THREAD_SIZE = 8192
    GPU_CORE_TOTAL_THREAD_SIZE = Config.CONFIG_CUDA_ThreadCount
    
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

    # print('Thread Block size X, Y, Z are ' + str(GPU_CORE_BLOCK_SIZE_X) + ', ' + str(GPU_CORE_BLOCK_SIZE_Y) + ', ' + str(GPU_CORE_BLOCK_SIZE_Z))
    # print('Total Thread Block size is ' + str(GPU_CORE_BLOCK_SIZE_X * GPU_CORE_BLOCK_SIZE_Y * GPU_CORE_BLOCK_SIZE_Z))
        
    GPU_CORE_BLOCK_SIZE = min(1024,GPU_CORE_TOTAL_THREAD_SIZE)
    GPU_CORE_GRID_SIZE = math.ceil(GPU_CORE_TOTAL_THREAD_SIZE / 1024)
        
    print('GPU_CORE_TOTAL_THREAD_SIZE is ' + str(GPU_CORE_TOTAL_THREAD_SIZE) + 'GPU_CORE_BLOCK_SIZE is ' + str(GPU_CORE_BLOCK_SIZE) + ', GPU_CORE_GRID_SIZE is' + str(GPU_CORE_GRID_SIZE))
        
    # TRADE_RESULT_COLUMNS = ['long short flag', 'ticker id', 'entry time id', 'entry price', 'exit time id', 'exit price', 'obs period', 'sharpe ratio threshold', 'exit sharpe ratio offset', 'stop loss', 'take profit', 'max holding period', 'section', 'sharpe in obs period at entry', 'while loop count']
    TRADE_RESULT_COLUMNS = ['long short flag', 'ticker id', 'entry time id', 'entry price', 'exit time id', 'exit price', 'obs period', 'sharpe ratio threshold', 'exit sharpe ratio offset', 'stop loss', 'take profit', 'max holding period', 'volume to mean volume ratio', 'min return per time slot']
    TRADE_RESULT_COLUMN_COUNT = len(TRADE_RESULT_COLUMNS)
    block_cutting_by_time = 0
    ErrorCode = 0

    scenario_column = {'obs period':ObsPeriod, 'sharpe ratio threshold':SharpeRatioThreshold, 'exit sharpe ratio offset':ExitSharpeRatioOffset, 'stop loss':StopLossPerTrade, 'take profit':TakeProfitPerTrade, 'max holding period':MaxHoldingPeriod, 'volume to mean volume ratio':VolumeToMeanVolumeRatio, 'min return per time slot':MinReturnPerTimeSlotThreshold}

    if TradeFilterIndicatorName is None:
        # TradeFilterIndicatorCount = 0
        TradeFilterIndicatorParameterCount = 0
        TradeFilterIndicatorThresholdCount = 0
        TradeFilterIndicatorParameter_matrix = np.array([0]).astype(np.float32)
        TradeFilterIndicatorThreshold_matrix = np.array([0]).astype(np.float32)
        
    else:
        scenario_column['indicator ' + TradeFilterIndicatorName] = TradeFilterIndicatorParameter
        scenario_column['indicator ' + TradeFilterIndicatorName + ' threshold'] = TradeFilterIndicatorThreshold
        # TradeFilterIndicatorCount = len(TradeFilterIndicatorParameter)
        TradeFilterIndicatorParameterCount = len(TradeFilterIndicatorParameter)
        TradeFilterIndicatorThresholdCount = len(TradeFilterIndicatorThreshold)
        TradeFilterIndicatorParameter_matrix = np.array(TradeFilterIndicatorParameter).astype(np.float32)
        TradeFilterIndicatorThreshold_matrix = np.array(TradeFilterIndicatorThreshold).astype(np.float32)

    TradeFilterIndicatorParameter_matrix_gpu = cuda.mem_alloc(TradeFilterIndicatorParameter_matrix.nbytes)
    TradeFilterIndicatorThreshold_matrix_gpu = cuda.mem_alloc(TradeFilterIndicatorThreshold_matrix.nbytes)
    cuda.memcpy_htod(TradeFilterIndicatorParameter_matrix_gpu, TradeFilterIndicatorParameter_matrix)
    cuda.memcpy_htod(TradeFilterIndicatorThreshold_matrix_gpu, TradeFilterIndicatorThreshold_matrix)


    print('TradeFilterIndicatorParameter_matrix is with dimension ' + str(len(TradeFilterIndicatorParameter_matrix)))
    # print(TradeFilterIndicatorParameter_matrix)
    TradeFilterIndicatorParameter_matrix_gpu = cuda.mem_alloc(TradeFilterIndicatorParameter_matrix.nbytes)
    cuda.memcpy_htod(TradeFilterIndicatorParameter_matrix_gpu, TradeFilterIndicatorParameter_matrix)

    print('TradeFilterIndicatorThreshold_matrix is with dimension ' + str(len(TradeFilterIndicatorThreshold_matrix)))
    # print(TradeFilterIndicatorThreshold_matrix)
    TradeFilterIndicatorThreshold_matrix_gpu = cuda.mem_alloc(TradeFilterIndicatorThreshold_matrix.nbytes)
    cuda.memcpy_htod(TradeFilterIndicatorThreshold_matrix_gpu, TradeFilterIndicatorThreshold_matrix)
        

    print('len(close_price_matrix) is ' + str(len(close_price_matrix)) + ' and scenario_column is ' + str(scenario_column))
    ticker_count = len(close_price_matrix)
    scenario_matrix = InitialiseScenarioMatrix(ticker_count, scenario_column)
    # print('scenario_matrix is')
    # print(scenario_matrix)

# 1010103
# 1010109

    scenario_column_count = len(scenario_column) + 1
    scenario_count = len(scenario_matrix)
    print('scenario_matrix is with dimension ' + str(len(scenario_matrix)) + ' x ' + str(len(scenario_matrix[0])))
    # scenario_matrix is with dimension 2592 x 9
    # print(scenario_matrix)
    # df = pd.DataFrame(data=scenario_matrix, columns=['ticker id', 'obs period', 'sharpe ratio threshold', 'exit sharpe ratio offset', 'stop loss', 'take profit', 'max holding period', 'volume to mean volume ratio', 'min return per time slot'])
    # df.to_csv(r'E:\TradeAnalysisProject\RoutineAnalysis\SharpeRatioStrategy\Debug\scenario_matrix.csv', index=False)


    print('time_std_unit_to_market_time_section_id_matrix is with dimension ' + str(len(time_std_unit_to_market_time_section_id_matrix)) + ' x ' + str(len(time_std_unit_to_market_time_section_id_matrix[0])))
    # time_std_unit_to_market_time_section_id_matrix is with dimension 1440 x 1
    # print(time_std_unit_to_market_time_section_id_matrix)
    # df = pd.DataFrame(data=time_std_unit_to_market_time_section_id_matrix, columns=['market_time_section_id'])
    # df.to_csv(r'E:\TradeAnalysisProject\RoutineAnalysis\SharpeRatioStrategy\Debug\time_std_unit_to_market_time_section_id_matrix.csv', index=False)
    
    print('mean_vol_by_market_time_section_id_matrix is with dimension ' + str(len(mean_vol_by_market_time_section_id_matrix)) + ' x ' + str(len(mean_vol_by_market_time_section_id_matrix[0])))
    market_time_section_id_count =  len(mean_vol_by_market_time_section_id_matrix[0])
    
    # mean_vol_by_market_time_section_id_matrix is with dimension 2 x 6
    # print(mean_vol_by_market_time_section_id_matrix)
    # col_list = []
    # for i in range(len(mean_vol_by_market_time_section_id_matrix[0])):
    #     col_list = col_list + ['col ' + str(i+1)]
    # df = pd.DataFrame(data=mean_vol_by_market_time_section_id_matrix, columns=[col_list])
    # df.to_csv(r'E:\TradeAnalysisProject\RoutineAnalysis\SharpeRatioStrategy\Debug\mean_vol_by_market_time_section_id_matrix.csv', index=False)

    if block_cutting_dimension == "Time Dimension":
        close_price_matrix = close_price_matrix.T.copy(order="C")
        volume_matrix = volume_matrix.T.copy(order="C")
        date_id_matrix = date_id_matrix.T.copy(order="C")
        time_std_unit_matrix = time_std_unit_matrix.T.copy(order="C")
        block_cutting_by_time = 1

    print('close_price_matrix is with dimension ' + str(len(close_price_matrix)) + ' x ' + str(len(close_price_matrix[0])))
    # close_price_matrix is with dimension 644165 x 2
    # print(close_price_ma1trix)

    # df = pd.DataFrame(data=close_price_matrix, columns=['ticker 0', 'ticker 1'])
    # df.to_csv(r'E:\TradeAnalysisProject\RoutineAnalysis\SharpeRatioStrategy\Debug\close_price_matrix.csv', index=False)

    # print('time_std_unit_matrix is')
    # print(time_std_unit_matrix)
    print('time_std_unit_matrix is with dimension ' + str(len(time_std_unit_matrix)) )

    # df = pd.DataFrame(data=time_std_unit_matrix, columns=['time in std unit'])
    # df.to_csv(r'E:\TradeAnalysisProject\RoutineAnalysis\SharpeRatioStrategy\Debug\time_std_unit_matrix.csv', index=False)

    print('date_id_matrix is with dimension ' + str(len(date_id_matrix)) )

    # df = pd.DataFrame(data=date_id_matrix, columns=['date id'])
    # df.to_csv(r'E:\TradeAnalysisProject\RoutineAnalysis\SharpeRatioStrategy\Debug\date_id_matrix.csv', index=False)


    SharpeRatioThreshold_size = len(SharpeRatioThreshold)
    ExitSharpeRatioOffset_size = len(ExitSharpeRatioOffset)

    # InitialResultCacheSize = InitialResultCacheSizeForOneObsPeriodMovementThreshold * ObsPeriodMovementThreshold_size
    # print('InitialResultCacheSize is ' + str(InitialResultCacheSize))
    print('InitialResultCacheSize is ' +  f"{InitialResultCacheSize:,}")
    # InitialResultCacheSize is 100,000,000

    first_dimension_size = len(close_price_matrix)
    second_dimension_size = len(close_price_matrix[0])
    print('first_dimension_size = ' + str(first_dimension_size) + ' and second_dimension_size = ' + str(second_dimension_size))
    # first_dimension_size = 644165 and second_dimension_size = 2

    # gpu_core_block_count = math.ceil(first_dimension_size/GPU_CORE_BLOCK_SIZE) 
    gpu_core_block_count = math.ceil(scenario_count/(GPU_CORE_BLOCK_SIZE * GPU_CORE_GRID_SIZE))
    
    # trade_result_count = np.int32(0) 
    trade_result_count = np.zeros(1, dtype=np.int32)

    trade_record_out = np.zeros((InitialResultCacheSize, TRADE_RESULT_COLUMN_COUNT)).astype(np.float32) #'long short flag', 'ticker id', 'entry time id', 'entry price', 'exit time id', 'exit price', 'obs period', 'sharpe ratio threshold', 'exit sharpe ratio offset', 'stop loss', 'take profit', 'stop time id'   
    print('TRADE_RESULT_COLUMN_COUNT is ' + str(TRADE_RESULT_COLUMN_COUNT) + ' at ' + str(datetime.now()))
    
    close_price_matrix = close_price_matrix.astype(np.float32)
    volume_matrix = volume_matrix.astype(np.float32)
    date_id_matrix = date_id_matrix.astype(np.float32)
    time_std_unit_matrix = time_std_unit_matrix.astype(np.float32)

    # e = time_std_unit_matrix.astype(np.float32)
    # a_out = a_out.astype(np.float32)

    close_price_matrix_gpu = cuda.mem_alloc(close_price_matrix.nbytes)
    volume_matrix_gpu = cuda.mem_alloc(volume_matrix.nbytes)
    date_id_matrix_gpu = cuda.mem_alloc(date_id_matrix.nbytes)
    time_std_unit_matrix_gpu = cuda.mem_alloc(time_std_unit_matrix.nbytes)
    trade_result_count_gpu = cuda.mem_alloc(trade_result_count.nbytes)
    scenario_matrix_gpu = cuda.mem_alloc(scenario_matrix.nbytes)
    time_std_unit_to_market_time_section_id_matrix_gpu = cuda.mem_alloc(time_std_unit_to_market_time_section_id_matrix.nbytes)
    mean_vol_by_market_time_section_id_matrix_gpu = cuda.mem_alloc(mean_vol_by_market_time_section_id_matrix.nbytes)
    

    # e_gpu = cuda.mem_alloc(e.nbytes)

    trade_record_out_gpu = cuda.mem_alloc(trade_record_out.nbytes)

    cuda.memcpy_htod(close_price_matrix_gpu, close_price_matrix)
    cuda.memcpy_htod(volume_matrix_gpu, volume_matrix)
    cuda.memcpy_htod(date_id_matrix_gpu, date_id_matrix)
    cuda.memcpy_htod(time_std_unit_matrix_gpu, time_std_unit_matrix)
    cuda.memcpy_htod(trade_result_count_gpu, trade_result_count)
    cuda.memcpy_htod(scenario_matrix_gpu, scenario_matrix)
    cuda.memcpy_htod(time_std_unit_to_market_time_section_id_matrix_gpu, time_std_unit_to_market_time_section_id_matrix)
    cuda.memcpy_htod(mean_vol_by_market_time_section_id_matrix_gpu, mean_vol_by_market_time_section_id_matrix)

    # cuda.memcpy_htod(e_gpu, e)

    cuda.memcpy_htod(trade_record_out_gpu, trade_record_out)

    AdditionalResultCount = np.zeros(1, dtype=np.int32)
    AdditionalResultCount_gpu = cuda.mem_alloc(AdditionalResultCount.nbytes)
    cuda.memcpy_htod(AdditionalResultCount_gpu, AdditionalResultCount)

    print('Start CUDA calculation at ' + str(datetime.now()))
    
    mod = SourceModule("""
      #include <cstdlib>
      #include <cmath>  

//      __device__ int add_trade( int *trade_result_count, int TRADE_RESULT_COLUMN_COUNT, float *trade_result, int long_short_flag, int ticker_id, int entry_time_id, float entry_price, int exit_time_id, float exit_price, int obs_period, float sharpe_ratio_threshold, float exit_sharpe_ratio_offset, float stop_loss, float take_profit, int max_holding_period, float volume_to_mean_volume_ratio, float min_return_per_time_slot, float *trade_filter_parameter_matrix, float trade_filter_threshold)
      __device__ int add_trade(unsigned long long *AdditionalResultCount, unsigned long long *trade_result_count, int TRADE_RESULT_COLUMN_COUNT, float *trade_result, int long_short_flag, int ticker_id, int entry_time_id, float entry_price, int exit_time_id, float exit_price, int obs_period, float sharpe_ratio_threshold, float exit_sharpe_ratio_offset, float stop_loss, float take_profit, int max_holding_period, float volume_to_mean_volume_ratio, float min_return_per_time_slot)
      {
        int trade_result_index, trade_result_index_offset, temp_AdditionalResultCount;
                        trade_result_index = atomicAdd(trade_result_count,1);
                        trade_result_index_offset = trade_result_index * TRADE_RESULT_COLUMN_COUNT ;
                        trade_result[trade_result_index_offset + 0] = long_short_flag;
                        trade_result[trade_result_index_offset + 1] = ticker_id;
                        trade_result[trade_result_index_offset + 2] = entry_time_id;
                        trade_result[trade_result_index_offset + 3] = entry_price;
                        trade_result[trade_result_index_offset + 4] = exit_time_id;
                        trade_result[trade_result_index_offset + 5] = exit_price;
                        trade_result[trade_result_index_offset + 6] = obs_period;
                        trade_result[trade_result_index_offset + 7] = sharpe_ratio_threshold;
                        trade_result[trade_result_index_offset + 8] = exit_sharpe_ratio_offset;
                        trade_result[trade_result_index_offset + 9] = stop_loss;
                        trade_result[trade_result_index_offset + 10] = take_profit;
                        trade_result[trade_result_index_offset + 11] = max_holding_period;
                        trade_result[trade_result_index_offset + 12] = volume_to_mean_volume_ratio;
                        trade_result[trade_result_index_offset + 13] = min_return_per_time_slot;
                        
//                        for (int i = 14; i<TRADE_RESULT_COLUMN_COUNT-1; i++) {
//                          trade_result[trade_result_index_offset + i] = trade_filter_parameter_matrix[i-14];
//                        }
//                        trade_result[TRADE_RESULT_COLUMN_COUNT-1] = trade_filter_threshold;

                        temp_AdditionalResultCount = atomicAdd(AdditionalResultCount,1);

                    return 0;
      }

      __device__ float get_mean_in_obs_period( int start_time_id, int end_time_id, int ticker_size, int ticker_id, float *close_data)
      {
        float mean_in_obs_period;
        mean_in_obs_period = 0;
        for (int obs_time_id = start_time_id + 1; obs_time_id <= end_time_id; obs_time_id++) {
          mean_in_obs_period = mean_in_obs_period + (close_data[obs_time_id * ticker_size + ticker_id] - close_data[(obs_time_id - 1) * ticker_size + ticker_id]) / close_data[(obs_time_id - 1) * ticker_size + ticker_id];
        }
        return mean_in_obs_period / (end_time_id - start_time_id);
      }

      __device__ float get_stdev_in_obs_period( int start_time_id, int end_time_id, int ticker_size, int ticker_id, float *close_data, float mean_in_obs_period)
      {
        float stdev_in_obs_period;
        stdev_in_obs_period = 0;
        for (int obs_time_id = start_time_id + 1; obs_time_id <= end_time_id; obs_time_id++) {
          stdev_in_obs_period = stdev_in_obs_period + pow( (close_data[obs_time_id * ticker_size + ticker_id] - close_data[(obs_time_id - 1) * ticker_size + ticker_id]) / close_data[(obs_time_id - 1) * ticker_size + ticker_id] - mean_in_obs_period, 2);
        }
        return pow(stdev_in_obs_period / (end_time_id - start_time_id), 0.5);
      }

      __device__ float get_sharpe_ratio( int start_time_id, int end_time_id, int ticker_size, int ticker_id, float *close_data, float min_mean_in_obs_period)
      {
        float mean_in_obs_period, stdev_in_obs_period;
        mean_in_obs_period = get_mean_in_obs_period(start_time_id, end_time_id, ticker_size, ticker_id, close_data);

        if (abs(mean_in_obs_period) < min_mean_in_obs_period) {
          return 0;
        }
        stdev_in_obs_period = get_stdev_in_obs_period( start_time_id, end_time_id, ticker_size, ticker_id, close_data, mean_in_obs_period);
        if (mean_in_obs_period == 0) {
          return 0;
        } else {
          return mean_in_obs_period / (stdev_in_obs_period + 0.00000001);
        }
      }

//      __global__ void sharpe_ratio_strategy_analysis(unsigned long long *AdditionalResultCount, int block_cutting_by_time, int second_dimension_size, int time_in_std_unit_per_day, int GPU_CORE_BLOCK_SIZE_X, int GPU_CORE_BLOCK_SIZE_Y, int GPU_CORE_BLOCK_SIZE_Z, int gpu_core_block_count, int first_dimension_size, int scenario_count, int scenario_column_count, int trade_filter_parameter_size, int trade_filter_threshold_size, int ErrorCode, int TRADE_RESULT_COLUMN_COUNT, unsigned long long *trade_result_count, float *close_data, float *volume_data, float *date_id_data, float *time_std_unit_matrix, float *time_std_unit_to_market_time_section_id_matrix, float *mean_vol_by_market_time_section_id_matrix, float *scenario_matrix, float *trade_result, float *trade_filter_parameter_matrix, float *trade_filter_threshold_matrix)
      __global__ void sharpe_ratio_strategy_analysis(unsigned long long *AdditionalResultCount, int block_cutting_by_time, int second_dimension_size, int market_time_section_id_count, int time_in_std_unit_per_day, int gpu_core_block_count, int first_dimension_size, int scenario_count, int scenario_column_count, int trade_filter_parameter_size, int trade_filter_threshold_size, int ErrorCode, int TRADE_RESULT_COLUMN_COUNT, unsigned long long *trade_result_count, float *close_data, float *volume_data, float *date_id_data, float *time_std_unit_matrix, float *time_std_unit_to_market_time_section_id_matrix, float *mean_vol_by_market_time_section_id_matrix, float *scenario_matrix, float *trade_result, float *trade_filter_parameter_matrix, float *trade_filter_threshold_matrix)
      {
        ErrorCode = 0;
        int thread_Index, scenario_id, scenario_id_offset, ticker_id, obs_period, max_holding_period, obs_time_length_in_std_unit, long_short_flag, entry_time_id, trade_result_index, trade_result_index_offset, trade_sign, time_std_unit, market_time_section_id;
        float sharpe_ratio_threshold, exit_sharpe_ratio_offset, stop_loss, take_profit, mean_in_obs_period, volume_to_mean_volume_ratio, min_return_per_time_slot, stdev_in_obs_period, sharpe_in_obs_period, entry_price, exit_price, pnl_per_unit_of_trade, sharpe_in_obs_period_at_entry, mean_vol, vol_at_time_id;
        bool exit_trade_done;
        
        thread_Index = blockIdx.x * blockDim.x + threadIdx.x;
        

        if (block_cutting_by_time == 1) {
          for (int k = 0; k < gpu_core_block_count; k++) {
            scenario_id = k * blockDim.x * gridDim.x + thread_Index;
            if (scenario_id < scenario_count) {
              scenario_id_offset = scenario_id * scenario_column_count;

              ticker_id = scenario_matrix[scenario_id_offset];
              obs_period = scenario_matrix[scenario_id_offset + 1];
              sharpe_ratio_threshold = scenario_matrix[scenario_id_offset + 2];
              exit_sharpe_ratio_offset = scenario_matrix[scenario_id_offset + 3];
              stop_loss = scenario_matrix[scenario_id_offset + 4];
              take_profit = scenario_matrix[scenario_id_offset + 5];
              max_holding_period = scenario_matrix[scenario_id_offset + 6];
              volume_to_mean_volume_ratio = scenario_matrix[scenario_id_offset + 7];
              min_return_per_time_slot = scenario_matrix[scenario_id_offset + 8];


              if (sharpe_ratio_threshold - exit_sharpe_ratio_offset >= 0) {
                for (int time_id = obs_period; time_id < first_dimension_size - 1; time_id++) {

                  time_std_unit = time_std_unit_matrix[time_id];
                  market_time_section_id = time_std_unit_to_market_time_section_id_matrix[time_std_unit];
//                  mean_vol = mean_vol_by_market_time_section_id_matrix[ticker_id * 6 + market_time_section_id + 1];
                  mean_vol = mean_vol_by_market_time_section_id_matrix[ticker_id * market_time_section_id_count + market_time_section_id];
                  
                  vol_at_time_id = volume_data[time_id * second_dimension_size + ticker_id];
                
                  obs_time_length_in_std_unit = time_in_std_unit_per_day * (date_id_data[time_id] - date_id_data[time_id - obs_period]) + time_std_unit_matrix[time_id] - time_std_unit_matrix[time_id - obs_period];
                        
   //                 add_trade(AdditionalResultCount, trade_result_count, TRADE_RESULT_COLUMN_COUNT, trade_result, -80, ticker_id, time_id - obs_period, obs_time_length_in_std_unit, time_id, time_std_unit_matrix[time_id], obs_period, sharpe_ratio_threshold, exit_sharpe_ratio_offset, stop_loss, take_profit, max_holding_period, volume_to_mean_volume_ratio, min_return_per_time_slot);

                  if ((obs_time_length_in_std_unit <= obs_period) && ( vol_at_time_id > volume_to_mean_volume_ratio * mean_vol)) {

                    long_short_flag = 0;
                   
                    sharpe_in_obs_period = get_sharpe_ratio(time_id - obs_period, time_id, second_dimension_size, ticker_id, close_data, min_return_per_time_slot);

                    if (sharpe_in_obs_period > sharpe_ratio_threshold) {
                      long_short_flag = 1;
                      entry_time_id = time_id;
                      entry_price = close_data[time_id * second_dimension_size + ticker_id];
                    } else if (sharpe_in_obs_period < -1 * sharpe_ratio_threshold) {
                      long_short_flag = -1;
                      entry_time_id = time_id;
                      entry_price = close_data[time_id * second_dimension_size + ticker_id];
                    }
                          
                    if (long_short_flag != 0) { 

                            

                      sharpe_in_obs_period_at_entry = sharpe_in_obs_period;
                      exit_trade_done = false;
                      while ((time_id < first_dimension_size - 1) && (time_id - entry_time_id < max_holding_period - 1)) {
                        time_id++;
                        
//                        obs_time_length_in_std_unit = time_std_unit_matrix[time_id * second_dimension_size + ticker_id] * (date_id_data[time_id * second_dimension_size + ticker_id] - date_id_data[entry_time_id * second_dimension_size + ticker_id]) - time_std_unit_matrix[entry_time_id * second_dimension_size + ticker_id];

                        obs_time_length_in_std_unit = time_in_std_unit_per_day * (date_id_data[time_id] - date_id_data[time_id - obs_period]) + time_std_unit_matrix[time_id] - time_std_unit_matrix[time_id - obs_period];
  
                        if (obs_time_length_in_std_unit > time_id - entry_time_id) {
                          break;
                        }
                        if (long_short_flag > 0) {
                          pnl_per_unit_of_trade = (close_data[time_id * second_dimension_size + ticker_id] - entry_price) / entry_price;
                        } else if (long_short_flag < 0) {
                          pnl_per_unit_of_trade = -1 * (close_data[time_id * second_dimension_size + ticker_id] - entry_price) / entry_price;
                        }
                      
                        if (((stop_loss != 0) && ( pnl_per_unit_of_trade < stop_loss * -1)) || ((take_profit != 0) && ( pnl_per_unit_of_trade > take_profit))) {
                          add_trade(AdditionalResultCount, trade_result_count, TRADE_RESULT_COLUMN_COUNT, trade_result, long_short_flag, ticker_id, entry_time_id, entry_price, time_id, close_data[time_id * second_dimension_size + ticker_id], obs_period, sharpe_ratio_threshold, exit_sharpe_ratio_offset, stop_loss, take_profit, max_holding_period, volume_to_mean_volume_ratio, min_return_per_time_slot);
                          exit_trade_done = true;
                          break;
                        }

                        sharpe_in_obs_period = get_sharpe_ratio(time_id - obs_period, time_id, second_dimension_size, ticker_id, close_data, min_return_per_time_slot);
 
                        if (long_short_flag > 0) {
                          trade_sign = 1;
                        } else if (long_short_flag < 0) {
                          trade_sign = -1;
                        }

                        if (trade_sign * sharpe_in_obs_period < sharpe_ratio_threshold - exit_sharpe_ratio_offset) {
                          add_trade(AdditionalResultCount, trade_result_count, TRADE_RESULT_COLUMN_COUNT, trade_result, long_short_flag, ticker_id, entry_time_id, entry_price, time_id, close_data[time_id * second_dimension_size + ticker_id], obs_period, sharpe_ratio_threshold, exit_sharpe_ratio_offset, stop_loss, take_profit, max_holding_period, volume_to_mean_volume_ratio, min_return_per_time_slot);
                          exit_trade_done = true;
                          break;
                        }
                      
                      }
                      
                      if (!exit_trade_done) {
                         add_trade(AdditionalResultCount, trade_result_count, TRADE_RESULT_COLUMN_COUNT, trade_result, long_short_flag, ticker_id, entry_time_id, entry_price, time_id, close_data[time_id * second_dimension_size + ticker_id], obs_period, sharpe_ratio_threshold, exit_sharpe_ratio_offset, stop_loss, take_profit, max_holding_period, volume_to_mean_volume_ratio, min_return_per_time_slot);
                         exit_trade_done = true;
                      }                            
                    }
                  }
                }
              }
            }
          }
        }
      }

      """)

    func = mod.get_function("sharpe_ratio_strategy_analysis")
    # func(AdditionalResultCount_gpu, np.int32(block_cutting_by_time), np.int32(second_dimension_size), np.int32(time_in_std_unit_per_day), np.int32(GPU_CORE_BLOCK_SIZE_X), np.int32(GPU_CORE_BLOCK_SIZE_Y), np.int32(GPU_CORE_BLOCK_SIZE_Z), np.int32(gpu_core_block_count), np.int32(first_dimension_size), np.int32(scenario_count), np.int32(scenario_column_count), np.int32(TradeFilterIndicatorParameterCount), np.int32(TradeFilterIndicatorThresholdCount), np.int32(ErrorCode), np.int32(TRADE_RESULT_COLUMN_COUNT), trade_result_count_gpu, close_price_matrix_gpu, volume_matrix_gpu, date_id_matrix_gpu, time_std_unit_matrix_gpu, time_std_unit_to_market_time_section_id_matrix_gpu, mean_vol_by_market_time_section_id_matrix_gpu, scenario_matrix_gpu, trade_record_out_gpu, TradeFilterIndicatorParameter_matrix_gpu, TradeFilterIndicatorThreshold_matrix_gpu, block=(GPU_CORE_BLOCK_SIZE_X,GPU_CORE_BLOCK_SIZE_Y,GPU_CORE_BLOCK_SIZE_Z))
    func(AdditionalResultCount_gpu, np.int32(block_cutting_by_time), np.int32(second_dimension_size), np.int32(market_time_section_id_count), np.int32(time_in_std_unit_per_day), np.int32(gpu_core_block_count), np.int32(first_dimension_size), np.int32(scenario_count), np.int32(scenario_column_count), np.int32(TradeFilterIndicatorParameterCount), np.int32(TradeFilterIndicatorThresholdCount), np.int32(ErrorCode), np.int32(TRADE_RESULT_COLUMN_COUNT), trade_result_count_gpu, close_price_matrix_gpu, volume_matrix_gpu, date_id_matrix_gpu, time_std_unit_matrix_gpu, time_std_unit_to_market_time_section_id_matrix_gpu, mean_vol_by_market_time_section_id_matrix_gpu, scenario_matrix_gpu, trade_record_out_gpu, TradeFilterIndicatorParameter_matrix_gpu, TradeFilterIndicatorThreshold_matrix_gpu, block=(GPU_CORE_BLOCK_SIZE,1,1), grid=(GPU_CORE_GRID_SIZE, 1))

    AdditionalResultCount_out = np.empty_like(AdditionalResultCount)
    cuda.memcpy_dtoh(AdditionalResultCount_out, AdditionalResultCount_gpu)

    print('AdditionalResultCount_out[0] is ' + f"{AdditionalResultCount_out[0]:,}")
    print() 
 
    trade_result_count_out = np.empty_like(trade_result_count)
    cuda.memcpy_dtoh(trade_result_count_out, trade_result_count_gpu)
    # print('trade result count is ' + str(trade_result_count_out))
    print('trade_result_count_out[0] = ' + f"{trade_result_count_out[0]:,}" + ' and InitialResultCacheSize is ' + f"{InitialResultCacheSize:,}" + ' and AdditionalResultCount_out[0] is ' + f"{AdditionalResultCount_out[0]:,}" + ' at ' + str(datetime.now()))

    trade_record = np.empty_like(trade_record_out)
    cuda.memcpy_dtoh(trade_record, trade_record_out_gpu)

    close_price_matrix_gpu.free()
    volume_matrix_gpu.free()
    date_id_matrix_gpu.free()
    time_std_unit_matrix_gpu.free()
    trade_result_count_gpu.free()
    scenario_matrix_gpu.free()
    time_std_unit_to_market_time_section_id_matrix_gpu.free()
    mean_vol_by_market_time_section_id_matrix_gpu.free()


    
    # print('trade record is')
    # print(trade_record)
    # trade_record = trade_record[0:trade_result_count_out]
    trade_record = trade_record[0:AdditionalResultCount_out[0]]
    # print('trade record after cut is')
    # print(trade_record)
    df = pd.DataFrame(data=trade_record, columns=TRADE_RESULT_COLUMNS)
    # print(df)
    # df.to_csv(r'E:\TradeAnalysisProject\RoutineAnalysis\SharpeRatioStrategy\Debug\trade_record.csv', index=False)
    return df