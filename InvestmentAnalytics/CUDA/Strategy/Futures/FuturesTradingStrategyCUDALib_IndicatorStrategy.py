# -*- coding: utf-8 -*-
"""
Created on Fri Oct  8 16:14:22 2021

@author: Henry Cheung
"""


import pycuda.driver as cuda
import pycuda.autoinit
from pycuda.compiler import SourceModule
import math
import pandas as pd

import InvestmentAnalytics.CUDA.CUDAPathSetting
import numpy as np
from InvestmentAnalytics.Indicator.Indicator import Indicator
import InvestmentAnalytics.Config as Config

GPU_CORE_TOTAL_THREAD_SIZE = Config.CONFIG_CUDA_ThreadCount
GPU_CORE_BLOCK_SIZE = min(1024,GPU_CORE_TOTAL_THREAD_SIZE)
GPU_CORE_GRID_SIZE = math.ceil(GPU_CORE_TOTAL_THREAD_SIZE / 1024)


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

def InitialiseScenarioMatrix(ticker_count, indicator_parameter_set_count, scenario_labels_dict):
    ticker_list = []
    for i in range(ticker_count):
        ticker_list.append(i)
    scenario_df = pd.DataFrame(ticker_list,columns =['ticker id'])
    scenario_df['Dummy'] = 1
    indicator_parameter_set_id_list = []
    for i in range(indicator_parameter_set_count):
        indicator_parameter_set_id_list.append(i)
    df = pd.DataFrame(indicator_parameter_set_id_list,columns =['indicator parameter id'])
    df['Dummy'] = 1
    scenario_df = scenario_df.merge(df, on='Dummy')
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
    

# def CUDASharpeRatioStrategy(close_price_matrix, volume_matrix, date_id_matrix, time_std_unit_matrix, time_std_unit_to_market_time_section_id_matrix, mean_vol_by_market_time_section_id_matrix, StopLossPerTrade = [0, 0.0025, 0.005], TakeProfitPerTrade = [0, 0.0025, 0.005], MaxHoldingPeriod = [10], VolumeToMeanVolumeRatio = [3], MinReturnPerTimeSlotThreshold = [0.0001], ObsPeriod = [5, 10], SharpeRatioThreshold = [0.5, 1, 2], ExitSharpeRatioOffset = [0, 0.5], TradeFilterIndicatorName = None, TradeFilterIndicatorDataLabel = None, TradeFilterIndicatorParameterList = None, TradeFilterIndicatorThreshold = None, TradeFilterIndicator_matrix_list = None, block_cutting_dimension = "Time Dimension", InitialResultCacheSize = 50000000):

# def CUDAIndicatorStrategy(close_price_matrix, indicator_matrix, IndicatorParameter, IndicatorType, IndicatorThreshold = [0.5, 1, 2], ExitIndicatorOffsetOffset = [0, 0.5], date_id_matrix = np.array([0]).astype(np.float32), time_std_unit_matrix = np.array([0]).astype(np.float32), time_std_unit_to_market_time_section_id_matrix = np.array([0]).astype(np.float32), StopLossPerTrade = [0, 0.0025, 0.005], TakeProfitPerTrade = [0, 0.0025, 0.005], MaxHoldingPeriod = [10], MinReturnPerTimeSlotThreshold = [0.0001], TradeFilterIndicatorName = None, TradeFilterIndicatorDataLabel = None, TradeFilterIndicatorParameterList = None, TradeFilterIndicatorThreshold = None, TradeFilterIndicator_matrix_list = None, block_cutting_dimension = "Time Dimension", InitialResultCacheSize = 50000000, volume_matrix=None, mean_vol_by_market_time_section_id_matrix=None, VolumeToMeanVolumeRatio = None):
# def CUDAIndicatorStrategy(close_price_matrix, indicator_matrix, indicator, IndicatorType, IndicatorThreshold = [0.5, 1, 2], ExitIndicatorOffsetOffset = [0, 0.5], date_id_matrix = np.array([0]).astype(np.float32), time_std_unit_matrix = np.array([0]).astype(np.float32), time_std_unit_to_market_time_section_id_matrix = np.array([0]).astype(np.float32), StopLossPerTrade = [0, 0.0025, 0.005], TakeProfitPerTrade = [0, 0.0025, 0.005], MaxHoldingPeriod = [10], MinReturnPerTimeSlotThreshold = [0.0001], TradeFilterIndicatorName = None, TradeFilterIndicatorDataLabel = None, TradeFilterIndicatorParameterList = None, TradeFilterIndicatorThreshold = None, TradeFilterIndicator_matrix_list = None, block_cutting_dimension = "Time Dimension", InitialResultCacheSize = 50000000, volume_matrix=None, mean_vol_by_market_time_section_id_matrix=None, VolumeToMeanVolumeRatio = None):
def CUDAIndicatorStrategy(close_price_matrix, indicator, IndicatorType, IndicatorThreshold = [0.5, 1, 2], ExitIndicatorOffsetOffset = [0, 0.5], date_id_matrix = np.array([0]).astype(np.float32), time_std_unit_matrix = np.array([0]).astype(np.float32), time_std_unit_to_market_time_section_id_matrix = np.array([0]).astype(np.float32), StopLossPerTrade = [0, 0.0025, 0.005], TakeProfitPerTrade = [0, 0.0025, 0.005], MaxHoldingPeriod = [10], MinReturnPerTimeSlotThreshold = [0.0001], TradeFilterIndicatorName = None, TradeFilterIndicatorDataLabel = None, TradeFilterIndicatorParameterList = None, TradeFilterIndicatorThreshold = None, TradeFilterIndicator_matrix_list = None, block_cutting_dimension = "Time Dimension", InitialResultCacheSize = 50000000, volume_matrix=np.array([[0]]).astype(np.float32), mean_vol_by_market_time_section_id_matrix=np.array([[0]]).astype(np.float32), VolumeToMeanVolumeRatio = 0):
    # TradeFilterIndicator_matrix_list = None
    # volume_matrix=None
    # mean_vol_by_market_time_section_id_matrix=None
    # VolumeToMeanVolumeRatio = None

    IndicatorParameter = indicator.IndicatorParameterList
    IndicatorParameterLabels = indicator.GetParameterLabelList()
    if block_cutting_dimension == "Time Dimension":
        # indicator_values = indicator.indicator_values
        # print('indicator_values[0] before transpose is with dimension ' + str(len(indicator_values[0])) + ' x ' + str(len(indicator_values[0][0])))
        # for indicator_value in indicator_values:
        #     indicator_value = indicator_value.T.copy(order="C")
        # print('indicator_values[0] after transpose is with dimension ' + str(len(indicator_values[0])) + ' x ' + str(len(indicator_values[0][0])))
            
        # indicator_matrix = np.vstack(indicator_values)
        
        print('indicator.indicator_values[0] before transpose is with dimension ' + str(len(indicator.indicator_values[0])) + ' x ' + str(len(indicator.indicator_values[0][0])))
        for indicator_value_index in range(len(indicator.indicator_values)):
            if indicator_value_index == 0:
                indicator_matrix = indicator.indicator_values[indicator_value_index].T.copy(order="C")
            else:
                indicator_matrix = np.concatenate((indicator_matrix, indicator.indicator_values[indicator_value_index].T.copy(order="C")), axis=0)
        print('indicator_matrix after transpose is with dimension ' + str(len(indicator_matrix)) + ' x ' + str(len(indicator_matrix[0])))
        
        
    else:
        indicator_matrix = np.vstack(indicator.indicator_values)

    print('IndicatorParameter is ' + str(IndicatorParameter))
    print('IndicatorThreshold is ' + str(IndicatorThreshold))
    print('indicator_matrix is with dimension ' + str(len(indicator_matrix)) + ' x ' + str(len(indicator_matrix[0])))
    # print(indicator_matrix)

    if TradeFilterIndicatorName is None:
        df_all = CUDAIndicatorStrategyPerFilterIndicator(close_price_matrix, indicator_matrix, IndicatorParameter, IndicatorParameterLabels, IndicatorType, IndicatorThreshold = IndicatorThreshold, ExitIndicatorOffsetOffset = ExitIndicatorOffsetOffset, date_id_matrix = date_id_matrix, time_std_unit_matrix = time_std_unit_matrix, time_std_unit_to_market_time_section_id_matrix = time_std_unit_to_market_time_section_id_matrix, StopLossPerTrade = StopLossPerTrade, TakeProfitPerTrade = TakeProfitPerTrade, MaxHoldingPeriod = MaxHoldingPeriod, MinReturnPerTimeSlotThreshold = MinReturnPerTimeSlotThreshold, TradeFilterIndicatorName = TradeFilterIndicatorName, TradeFilterIndicatorDataLabel = TradeFilterIndicatorDataLabel, TradeFilterIndicatorParameter = None, TradeFilterIndicatorThreshold = TradeFilterIndicatorThreshold, TradeFilterIndicator_matrix = None, block_cutting_dimension = block_cutting_dimension, InitialResultCacheSize = InitialResultCacheSize, volume_matrix = volume_matrix, mean_vol_by_market_time_section_id_matrix = mean_vol_by_market_time_section_id_matrix, VolumeToMeanVolumeRatio = VolumeToMeanVolumeRatio)
    else:
        df_all = pd.DataFrame()
        for i in range(len(TradeFilterIndicatorParameterList)):
            df = CUDAIndicatorStrategyPerFilterIndicator(close_price_matrix, indicator_matrix, IndicatorParameter, IndicatorParameterLabels, IndicatorType, IndicatorThreshold = IndicatorThreshold, ExitIndicatorOffsetOffset = ExitIndicatorOffsetOffset, date_id_matrix = date_id_matrix, time_std_unit_matrix = time_std_unit_matrix, time_std_unit_to_market_time_section_id_matrix = time_std_unit_to_market_time_section_id_matrix, StopLossPerTrade = StopLossPerTrade, TakeProfitPerTrade = TakeProfitPerTrade, MaxHoldingPeriod = MaxHoldingPeriod, MinReturnPerTimeSlotThreshold = MinReturnPerTimeSlotThreshold, TradeFilterIndicatorName = TradeFilterIndicatorName, TradeFilterIndicatorDataLabel = TradeFilterIndicatorDataLabel, TradeFilterIndicatorParameter = TradeFilterIndicatorParameterList[i], TradeFilterIndicatorThreshold = TradeFilterIndicatorThreshold, TradeFilterIndicator_matrix = TradeFilterIndicator_matrix_list[i], block_cutting_dimension = block_cutting_dimension, InitialResultCacheSize = InitialResultCacheSize, volume_matrix = volume_matrix, mean_vol_by_market_time_section_id_matrix = mean_vol_by_market_time_section_id_matrix, VolumeToMeanVolumeRatio = VolumeToMeanVolumeRatio)
            df_all = df_all.append(df)
            
    return df_all

    
    
def CUDAIndicatorStrategyPerFilterIndicator(close_price_matrix, indicator_matrix, IndicatorParameter, IndicatorParameterLabels, IndicatorType = 0, IndicatorThreshold = [0.5, 1, 2], ExitIndicatorOffsetOffset = [0, 0.5], date_id_matrix = np.array([0]).astype(np.float32), time_std_unit_matrix = np.array([0]).astype(np.float32), time_std_unit_to_market_time_section_id_matrix = np.array([0]).astype(np.float32), StopLossPerTrade = [0, 0.0025, 0.005], TakeProfitPerTrade = [0, 0.0025, 0.005], MaxHoldingPeriod = [10], MinReturnPerTimeSlotThreshold = [0.0001], TradeFilterIndicatorName = None, TradeFilterIndicatorDataLabel = None, TradeFilterIndicatorParameter = None, TradeFilterIndicatorThreshold = None, TradeFilterIndicator_matrix = None, block_cutting_dimension = "Time Dimension", InitialResultCacheSize = 50000000, volume_matrix=np.array([0]).astype(np.float32), mean_vol_by_market_time_section_id_matrix=np.array([0]).astype(np.float32), VolumeToMeanVolumeRatio = None):

    # TRADE_RESULT_COLUMNS = ['long short flag', 'ticker id', 'entry time id', 'entry price', 'exit time id', 'exit price', 'obs period', 'sharpe ratio threshold', 'exit sharpe ratio offset', 'stop loss', 'take profit', 'max holding period', 'section', 'sharpe in obs period at entry', 'while loop count']
    # TRADE_RESULT_COLUMNS = ['long short flag', 'ticker id', 'entry time id', 'entry price', 'exit time id', 'exit price', 'obs period', 'sharpe ratio threshold', 'exit sharpe ratio offset', 'stop loss', 'take profit', 'max holding period', 'volume to mean volume ratio', 'min return per time slot']
    # TRADE_RESULT_COLUMNS = ['long short flag', 'ticker id', 'entry time id', 'entry price', 'exit time id', 'exit price', 'indicator type', 'indicator threshold', 'exit indicator offset', 'stop loss', 'take profit', 'max holding period']
    TRADE_RESULT_COLUMNS = ['long short flag', 'ticker id', 'entry time id', 'entry price', 'exit time id', 'exit price', 'indicator type', 'indicator threshold', 'exit indicator offset', 'stop loss', 'take profit', 'max holding period', 'indicator value', 'indicator value used']
    for parameter_pos in range(len(IndicatorParameter[0])):
        # TRADE_RESULT_COLUMNS.append('indicator parameter ' + str(parameter_pos))
        TRADE_RESULT_COLUMNS.append('indicator param ' + IndicatorParameterLabels[parameter_pos])
    print('TRADE_RESULT_COLUMNS is')
    print(TRADE_RESULT_COLUMNS)
    TRADE_RESULT_COLUMN_COUNT = len(TRADE_RESULT_COLUMNS)
    block_cutting_by_time = 0
    ErrorCode = 0

    # scenario_column = {'obs period':ObsPeriod, 'sharpe ratio threshold':SharpeRatioThreshold, 'exit sharpe ratio offset':ExitSharpeRatioOffset, 'stop loss':StopLossPerTrade, 'take profit':TakeProfitPerTrade, 'max holding period':MaxHoldingPeriod, 'volume to mean volume ratio':VolumeToMeanVolumeRatio, 'min return per time slot':MinReturnPerTimeSlotThreshold}
    # scenario_column = {'indicator type':IndicatorType, 'indicator threshold':IndicatorThreshold, 'exit indicator offset':ExitIndicatorOffsetOffset, 'stop loss':StopLossPerTrade, 'take profit':TakeProfitPerTrade, 'max holding period':MaxHoldingPeriod, 'volume to mean volume ratio':VolumeToMeanVolumeRatio, 'min return per time slot':MinReturnPerTimeSlotThreshold}
    # scenario_column = {'indicator parameter':IndicatorParameter, 'indicator threshold':IndicatorThreshold, 'exit indicator offset':ExitIndicatorOffsetOffset, 'stop loss':StopLossPerTrade, 'take profit':TakeProfitPerTrade, 'max holding period':MaxHoldingPeriod}
    scenario_column = {'indicator threshold':IndicatorThreshold, 'exit indicator offset':ExitIndicatorOffsetOffset, 'stop loss':StopLossPerTrade, 'take profit':TakeProfitPerTrade, 'max holding period':MaxHoldingPeriod}

    indicator_count = len(indicator_matrix)
    print('indicator_count is ' + str(indicator_count))
    
    if TradeFilterIndicatorName is None:
        # TradeFilterIndicatorCount = 0
        TradeFilterIndicatorParameterCount = 0
        TradeFilterIndicatorThresholdCount = 0
        TradeFilterIndicatorParameter_matrix = np.array([0]).astype(np.float32)
        TradeFilterIndicatorThreshold_matrix = np.array([0]).astype(np.float32)
        
    else:
        scenario_column['filter indicator'] = TradeFilterIndicatorParameter
        scenario_column['filter indicator threshold'] = TradeFilterIndicatorThreshold
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
    
    if VolumeToMeanVolumeRatio is None:
        pass
        

    print('len(close_price_matrix) is ' + str(len(close_price_matrix)) + ' and scenario_column is ' + str(scenario_column))
    ticker_count = len(close_price_matrix)
    print('scenario_column is')
    print(scenario_column)
    scenario_matrix = InitialiseScenarioMatrix(ticker_count, len(IndicatorParameter), scenario_column)
    print('scenario_matrix is with dimension ' + str(len(scenario_matrix)) + ' x ' + str(len(scenario_matrix[0])))
    # print(scenario_matrix)

    # scenario_column_count = len(scenario_column) + 1
    scenario_count = len(scenario_matrix)
    scenario_column_count = len(scenario_matrix[0])
    print('scenario_matrix is with dimension ' + str(len(scenario_matrix)) + ' x ' + str(len(scenario_matrix[0])))
    # print(scenario_matrix)

    print('time_std_unit_to_market_time_section_id_matrix is with dimension ' + str(len(time_std_unit_to_market_time_section_id_matrix)) + ' x ' + str(len(time_std_unit_to_market_time_section_id_matrix[0])))
    # print(time_std_unit_to_market_time_section_id_matrix)
    
    print('mean_vol_by_market_time_section_id_matrix is with dimension ' + str(len(mean_vol_by_market_time_section_id_matrix)) + ' x ' + str(len(mean_vol_by_market_time_section_id_matrix[0])))
    # print(mean_vol_by_market_time_section_id_matrix)

    if block_cutting_dimension == "Time Dimension":
        close_price_matrix = close_price_matrix.T.copy(order="C")
        volume_matrix = volume_matrix.T.copy(order="C")
        date_id_matrix = date_id_matrix.T.copy(order="C")
        time_std_unit_matrix = time_std_unit_matrix.T.copy(order="C")
        block_cutting_by_time = 1

    print('close_price_matrix is with dimension ' + str(len(close_price_matrix)) + ' x ' + str(len(close_price_matrix[0])))
    # print(close_price_matrix)


    # IndicatorThreshold_size = len(IndicatorThreshold)
    # ExitSharpeRatioOffset_size = len(ExitSharpeRatioOffset)

    # InitialResultCacheSize = InitialResultCacheSizeForOneObsPeriodMovementThreshold * ObsPeriodMovementThreshold_size
    # print('InitialResultCacheSize is ' + str(InitialResultCacheSize))

    first_dimension_size = len(close_price_matrix)
    second_dimension_size = len(close_price_matrix[0])

    # gpu_core_block_count = math.ceil(first_dimension_size/GPU_CORE_BLOCK_SIZE) 
    gpu_core_block_count = math.ceil(first_dimension_size/(GPU_CORE_BLOCK_SIZE * GPU_CORE_GRID_SIZE)) 

    trade_result_count = np.int32(0) 

    trade_record_out = np.zeros((InitialResultCacheSize, TRADE_RESULT_COLUMN_COUNT)).astype(np.float32) #'long short flag', 'ticker id', 'entry time id', 'entry price', 'exit time id', 'exit price', 'obs period', 'sharpe ratio threshold', 'exit sharpe ratio offset', 'stop loss', 'take profit', 'stop time id'   
    close_price_matrix = close_price_matrix.astype(np.float32)
    volume_matrix = volume_matrix.astype(np.float32)
    date_id_matrix = date_id_matrix.astype(np.float32)
    time_std_unit_matrix = time_std_unit_matrix.astype(np.float32)
    paramter_set_matrix = np.array(IndicatorParameter).astype(np.float32)
    indicator_matrix = indicator_matrix.astype(np.float32)
    print('paramter_set_matrix is')
    # print(paramter_set_matrix)

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
    paramter_set_matrix_gpu = cuda.mem_alloc(paramter_set_matrix.nbytes)
    indicator_matrix_gpu = cuda.mem_alloc(indicator_matrix.nbytes)

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
    cuda.memcpy_htod(paramter_set_matrix_gpu, paramter_set_matrix)
    cuda.memcpy_htod(indicator_matrix_gpu, indicator_matrix)

    # cuda.memcpy_htod(e_gpu, e)

    cuda.memcpy_htod(trade_record_out_gpu, trade_record_out)



      
    mod = SourceModule("""
      #include <cstdlib>
      #include <cmath>

                       
//['long short flag', 'ticker id', 'entry time id', 'entry price', 'exit time id', 'exit price', 'indicator type', 'indicator threshold', 'exit indicator offset', 'stop loss', 'take profit', 'max holding period', 'indicator parameter 0', 'indicator parameter 1']    
      __device__ int add_trade( int *trade_result_count, int TRADE_RESULT_COLUMN_COUNT, float *trade_result, int long_short_flag, int ticker_id, int entry_time_id, float entry_price, int exit_time_id, float exit_price, int indicator_type, float indicator_threshold, float exit_indicator_offset, float stop_loss, float take_profit, int max_holding_period, int parameter_set_id, int number_of_indicator_parameter, float *indicator_parameter, float indicator_value, float indicator_value_used)
        {
        int trade_result_index, trade_result_index_offset;
                        trade_result_index = atomicAdd(trade_result_count,1);
                        trade_result_index_offset = trade_result_index * TRADE_RESULT_COLUMN_COUNT ;
                        trade_result[trade_result_index_offset + 0] = long_short_flag;
                        trade_result[trade_result_index_offset + 1] = ticker_id;
                        trade_result[trade_result_index_offset + 2] = entry_time_id;
                        trade_result[trade_result_index_offset + 3] = entry_price;
                        trade_result[trade_result_index_offset + 4] = exit_time_id;
                        trade_result[trade_result_index_offset + 5] = exit_price;
                        trade_result[trade_result_index_offset + 6] = indicator_type;
                        trade_result[trade_result_index_offset + 7] = indicator_threshold;
                        trade_result[trade_result_index_offset + 8] = exit_indicator_offset;
                        trade_result[trade_result_index_offset + 9] = stop_loss;
                        trade_result[trade_result_index_offset + 10] = take_profit;
                        trade_result[trade_result_index_offset + 11] = max_holding_period;
                        trade_result[trade_result_index_offset + 12] = indicator_value;
                        trade_result[trade_result_index_offset + 13] = indicator_value_used;
                        for (int i = 0; i<number_of_indicator_parameter; i++) {
                            trade_result[trade_result_index_offset + 14 + i] = indicator_parameter[parameter_set_id * number_of_indicator_parameter + i];
                        }
                    return 0;
      }


      __global__ void indicator_strategy_analysis(int block_cutting_by_time, int second_dimension_size, int gpu_core_block_count, int first_dimension_size, int scenario_count, int scenario_column_count, int number_of_indicator_parameter, int indicator_type, int trade_filter_parameter_size, int trade_filter_threshold_size, int ErrorCode, int TRADE_RESULT_COLUMN_COUNT, int *trade_result_count, float *close_data, float *indicator_parameter, float *indicator_matrix, float *volume_data, float *date_id_data, float *time_std_unit_matrix, float *time_std_unit_to_market_time_section_id_matrix, float *mean_vol_by_market_time_section_id_matrix, float *scenario_matrix, float *trade_result, float *trade_filter_parameter_matrix, float *trade_filter_threshold_matrix)
      {
        int thread_Index, scenario_id, scenario_id_offset, ticker_id, parameter_set_id, max_holding_period, indicator_matrix_offset, long_short_flag, entry_time_id, exit_time_id;
        float indicator_threshold, exit_indicator_offset, stop_loss, take_profit, close_price, entry_price, exit_price, indicator_value, indicator_value_used, entry_indicator_value, entry_indicator_value_used;
        ErrorCode = 0;

        thread_Index = blockIdx.x * blockDim.x + threadIdx.x;
        
        if (block_cutting_by_time == 1) {
          for (int k = 0; k < gpu_core_block_count; k++) {
            scenario_id = k * blockDim.x * gridDim.x + thread_Index;
            if (scenario_id < scenario_count) {
              scenario_id_offset = scenario_id * scenario_column_count;
              ticker_id = (int) scenario_matrix[scenario_id_offset];
              parameter_set_id = (int) scenario_matrix[scenario_id_offset + 1];
              indicator_threshold = scenario_matrix[scenario_id_offset + 2];
              exit_indicator_offset = scenario_matrix[scenario_id_offset + 3];
              stop_loss = scenario_matrix[scenario_id_offset + 4];
              take_profit = scenario_matrix[scenario_id_offset + 5];
              max_holding_period = scenario_matrix[scenario_id_offset + 6];
              indicator_matrix_offset = parameter_set_id * first_dimension_size * second_dimension_size + ticker_id;
              long_short_flag = 0;

              for (int time_id = 0; time_id < first_dimension_size; time_id++) {
              
                close_price = close_data[time_id * second_dimension_size + ticker_id];
                indicator_value = indicator_matrix[indicator_matrix_offset + time_id * second_dimension_size];
                
                if (indicator_type == 1) {
                  indicator_value_used = indicator_value / close_price;
                } else {
                  indicator_value_used = indicator_value;
                }
                
                if (long_short_flag == 0) {

//                  if (time_id < 20) {
//                    add_trade(trade_result_count, TRADE_RESULT_COLUMN_COUNT, trade_result, long_short_flag, 3, time_id, indicator_value, time_id, indicator_value_used, indicator_type, indicator_threshold, exit_indicator_offset, stop_loss, take_profit, max_holding_period, parameter_set_id, number_of_indicator_parameter, indicator_parameter, indicator_value, indicator_value_used);
//                  }
                  if ( indicator_value_used > indicator_threshold) {
                    entry_price = close_price;
                    entry_time_id = time_id;
                    entry_indicator_value = indicator_value;
                    entry_indicator_value_used = indicator_value_used;
                    long_short_flag = 1;
                  } else if ( - indicator_value_used > indicator_threshold) {
                    entry_price = close_price;
                    entry_time_id = time_id;
                    entry_indicator_value = indicator_value;
                    entry_indicator_value_used = indicator_value_used;
                    long_short_flag = -1;
                  }
                } else if (long_short_flag > 0) {
                  if ( indicator_value_used < indicator_threshold - exit_indicator_offset) {
                    add_trade(trade_result_count, TRADE_RESULT_COLUMN_COUNT, trade_result, long_short_flag, ticker_id, entry_time_id, entry_price, time_id, close_price, indicator_type, indicator_threshold, exit_indicator_offset, stop_loss, take_profit, max_holding_period, parameter_set_id, number_of_indicator_parameter, indicator_parameter, entry_indicator_value, entry_indicator_value_used);
                    long_short_flag = 0;
                  }
                } else if (long_short_flag < 0) {
                  if ( indicator_value_used > exit_indicator_offset - indicator_threshold) {
                    add_trade(trade_result_count, TRADE_RESULT_COLUMN_COUNT, trade_result, long_short_flag, ticker_id, entry_time_id, entry_price, time_id, close_price, indicator_type, indicator_threshold, exit_indicator_offset, stop_loss, take_profit, max_holding_period, parameter_set_id, number_of_indicator_parameter, indicator_parameter, entry_indicator_value, entry_indicator_value_used);
                    long_short_flag = 0;
                  }
                }
                
              }
            }
          }
        }

      }

      """)


    func = mod.get_function("indicator_strategy_analysis")
    func(np.int32(block_cutting_by_time), np.int32(second_dimension_size), np.int32(gpu_core_block_count), np.int32(first_dimension_size), np.int32(scenario_count), np.int32(scenario_column_count), np.int32(len(IndicatorParameter[0])), np.int32(IndicatorType), np.int32(TradeFilterIndicatorParameterCount), np.int32(TradeFilterIndicatorThresholdCount), np.int32(ErrorCode), np.int32(TRADE_RESULT_COLUMN_COUNT), trade_result_count_gpu, close_price_matrix_gpu, paramter_set_matrix_gpu, indicator_matrix_gpu, volume_matrix_gpu, date_id_matrix_gpu, time_std_unit_matrix_gpu, time_std_unit_to_market_time_section_id_matrix_gpu, mean_vol_by_market_time_section_id_matrix_gpu, scenario_matrix_gpu, trade_record_out_gpu, TradeFilterIndicatorParameter_matrix_gpu, TradeFilterIndicatorThreshold_matrix_gpu, block=(GPU_CORE_BLOCK_SIZE,1,1), grid=(GPU_CORE_GRID_SIZE, 1))
 
    trade_result_count_out = np.empty_like(trade_result_count)
    cuda.memcpy_dtoh(trade_result_count_out, trade_result_count_gpu)
    print('trade result count is ' + str(trade_result_count_out))

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
    paramter_set_matrix_gpu.free()
    indicator_matrix_gpu.free()

    
    # print('trade record is')
    # print(trade_record)
    trade_record = trade_record[0:trade_result_count_out]
    # print('trade record after cut is')
    # print(trade_record)
    df = pd.DataFrame(data=trade_record, columns=TRADE_RESULT_COLUMNS)
    # print(df)
    # df.to_csv(r'G:\TradeAnalysisProject\temp\trade_record.csv')
    return df