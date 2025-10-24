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
import numpy as np

# TOTAL_TIME_IN_STD_UNIT_PER_DAY = {"1 min":24*60, "10 secs":24*60*60}

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
    # indicator_parameter_set_id_list = []
    # for i in range(indicator_parameter_set_count):
    #     indicator_parameter_set_id_list.append(i)
    # df = pd.DataFrame(indicator_parameter_set_id_list,columns =['indicator parameter id'])
    # df['Dummy'] = 1
    # scenario_df = scenario_df.merge(df, on='Dummy')
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

    scenario_df.to_csv(r'G:\TradeAnalysisProject\temp\scenario_df.csv', index=False)
    scenario_matrix = scenario_df.to_numpy().astype(np.float32)
    return scenario_matrix.copy(order="C")


def CUDAMarketShockStrategy(close_price_matrix, volume_matrix, date_id_matrix, time_std_unit_matrix, return_mean_matrix, return_stdev_matrix, vol_mean_matrix, vol_stdev_matrix, StartTimeInStdUnit, EndTimeInStdUnit, MaxHoldingPeriodInStdUnitList, IR_TickersID_List, IR_Ticker_Volume_Stdev_Threshold, Non_IR_Ticker_Volume_Stdev_Threshold, IR_Ticker_Shock_Stdev_Threshold, Non_IR_Ticker_Shock_Stdev_Threshold, IR_Ticker_Shock_Count_Threshold, Non_IR_Ticker_Shock_Count_Threshold, StopLossSizeToShockRatio, FloatingStopLossMovement, block_cutting_dimension = "Time Dimension", InitialResultCacheSize = None, TimeFrame = "1 min", GPU_CORE_BLOCK_SIZE = 32*32):
    
    print('GPU_CORE_BLOCK_SIZE is ' + str(GPU_CORE_BLOCK_SIZE))
    # SCENARIO_COLUMNS = ['ticker id', 'IR Ticker Volume Stdev Threshold', 'Non IR Ticker Volume Stdev Threshold', 'IR Ticker Shock Stdev Threshold', 'Non IR Ticker Shock Stdev Threshold', 'IR Ticker Shock Count Threshold', 'Non IR Ticker Shock Count Threshold', 'Stop Loss Size to Shock Ratio', 'Floating StopLoss Movement']
    # TRADE_RESULT_COLUMNS = ['long short flag', 'ticker id', 'entry time id', 'entry price', 'exit time id', 'exit price', 'IR Ticker Volume Stdev Threshold', 'Non IR Ticker Volume Stdev Threshold', 'IR Ticker Shock Stdev Threshold', 'Non IR Ticker Shock Stdev Threshold', 'IR Ticker Shock Count Threshold', 'Non IR Ticker Shock Count Threshold', 'Stop Loss Size to Shock Ratio', 'Floating StopLoss Movement', 'Max Holding Period', 'stop time id']
    TRADE_RESULT_COLUMNS = ['long short flag', 'ticker id', 'entry time id', 'entry price', 'exit time id', 'exit price', 'IR Ticker Volume Stdev Threshold', 'Non IR Ticker Volume Stdev Threshold', 'IR Ticker Shock Stdev Threshold', 'Non IR Ticker Shock Stdev Threshold', 'IR Ticker Shock Count Threshold', 'Non IR Ticker Shock Count Threshold', 'Stop Loss Size to Shock Ratio', 'Floating StopLoss Movement', 'Max Holding Period', 'stop time id', 'ticker return mean', 'ticker return stdev', 'ticker vol mean', 'ticker vol stdev']
    TRADE_RESULT_COLUMN_COUNT = len(TRADE_RESULT_COLUMNS)
    block_cutting_by_time = 0
    ErrorCode = 0
    ticker_count = len(close_price_matrix)
    MaxHoldingPeriodInStdUnit = max(MaxHoldingPeriodInStdUnitList)


    scenario_column = {'IR Ticker Volume Stdev Threshold':IR_Ticker_Volume_Stdev_Threshold, 'Non IR Ticker Volume Stdev Threshold':Non_IR_Ticker_Volume_Stdev_Threshold, 'IR Ticker Shock Stdev Threshold':IR_Ticker_Shock_Stdev_Threshold, 'Non IR Ticker Shock Stdev Threshold':Non_IR_Ticker_Shock_Stdev_Threshold, 'IR Ticker Shock Count Threshold':IR_Ticker_Shock_Count_Threshold, 'Non IR Ticker Shock Count Threshold':Non_IR_Ticker_Shock_Count_Threshold, 'Stop Loss Size to Shock Ratio':StopLossSizeToShockRatio, 'Floating StopLoss Movement':FloatingStopLossMovement, 'Max Holding Period':MaxHoldingPeriodInStdUnitList}
    scenario_matrix = InitialiseScenarioMatrix(ticker_count, scenario_column)
    print("dimension of scenario_matrix is " + str(len(scenario_matrix)) + " x " + str(len(scenario_matrix[0])))
    print(scenario_matrix)
    scenario_count = len(scenario_matrix)
    scenario_column_count = len(scenario_matrix[0])

    if block_cutting_dimension == "Time Dimension":
        close_price_matrix = close_price_matrix.T.copy(order="C")
        volume_matrix = volume_matrix.T.copy(order="C")
        date_id_matrix = date_id_matrix.T.copy(order="C")
        time_std_unit_matrix = time_std_unit_matrix.T.copy(order="C")
        block_cutting_by_time = 1
        
    print("dimension of close_price_matrix is " + str(len(close_price_matrix)) + " x " + str(len(close_price_matrix[0])))
    print(close_price_matrix)
    print("dimension of date_id_matrix is " + str(len(date_id_matrix)))
    print(date_id_matrix)
    print("dimension of time_std_unit_matrix is " + str(len(time_std_unit_matrix)))
    print(time_std_unit_matrix)
        
    print('EndTimeInStdUnit is ' + str(EndTimeInStdUnit))
    print('StartTimeInStdUnit is ' + str(StartTimeInStdUnit))
    print('MaxHoldingPeriodInStdUnit is ' + str(MaxHoldingPeriodInStdUnit))
    print('ticker_count is ' + str(ticker_count))
    
    if InitialResultCacheSize is None:
        InitialResultCacheSize = 50000000

    print('InitialResultCacheSize is ' + str(InitialResultCacheSize))

    first_dimension_size = len(close_price_matrix)
    second_dimension_size = len(close_price_matrix[0])

    gpu_core_block_count = math.ceil(first_dimension_size/GPU_CORE_BLOCK_SIZE)

    trade_result_count = np.int32(0)

    trade_result = np.zeros((InitialResultCacheSize, TRADE_RESULT_COLUMN_COUNT)).astype(np.float32) #long short flag, ticker id, obs time id, entry time id, entry price, exit time id, exit price, trade id
    
    close_price_matrix = close_price_matrix.astype(np.float32)
    volume_matrix = volume_matrix.astype(np.float32)
    date_id_matrix = date_id_matrix.astype(np.float32)
    
    time_std_unit_matrix = time_std_unit_matrix.astype(np.float32)
    
    return_mean_matrix = return_mean_matrix.astype(np.float32)
    return_stdev_matrix = return_stdev_matrix.astype(np.float32)
    vol_mean_matrix = vol_mean_matrix.astype(np.float32)
    vol_stdev_matrix = vol_stdev_matrix.astype(np.float32)
    
    IR_TickersID_List_matrix = np.array(IR_TickersID_List)
    IR_TickersID_List_count = len(IR_TickersID_List)
    
    IR_TickersID_List_matrix = IR_TickersID_List_matrix.astype(np.int32)
    
    close_price_matrix_gpu = cuda.mem_alloc(close_price_matrix.nbytes)
    volume_matrix_gpu = cuda.mem_alloc(volume_matrix.nbytes)
    date_id_matrix_gpu = cuda.mem_alloc(date_id_matrix.nbytes)
    trade_result_count_gpu = cuda.mem_alloc(trade_result_count.nbytes)
    time_std_unit_matrix_gpu = cuda.mem_alloc(time_std_unit_matrix.nbytes)
    trade_result_gpu = cuda.mem_alloc(trade_result.nbytes)
    scenario_matrix_gpu = cuda.mem_alloc(scenario_matrix.nbytes)
    return_mean_matrix_gpu = cuda.mem_alloc(return_mean_matrix.nbytes)
    return_stdev_matrix_gpu = cuda.mem_alloc(return_stdev_matrix.nbytes)
    vol_mean_matrix_gpu = cuda.mem_alloc(vol_mean_matrix.nbytes)
    vol_stdev_matrix_gpu = cuda.mem_alloc(vol_stdev_matrix.nbytes)
    IR_TickersID_List_matrix_gpu = cuda.mem_alloc(IR_TickersID_List_matrix.nbytes)
    
    
    cuda.memcpy_htod(close_price_matrix_gpu, close_price_matrix)
    cuda.memcpy_htod(volume_matrix_gpu, volume_matrix)
    cuda.memcpy_htod(date_id_matrix_gpu, date_id_matrix)
    cuda.memcpy_htod(trade_result_count_gpu, trade_result_count)
    cuda.memcpy_htod(time_std_unit_matrix_gpu, time_std_unit_matrix)
    cuda.memcpy_htod(trade_result_gpu, trade_result)

    cuda.memcpy_htod(scenario_matrix_gpu, scenario_matrix)
    cuda.memcpy_htod(return_mean_matrix_gpu, return_mean_matrix)
    cuda.memcpy_htod(return_stdev_matrix_gpu, return_stdev_matrix)
    cuda.memcpy_htod(vol_mean_matrix_gpu, vol_mean_matrix)
    cuda.memcpy_htod(vol_stdev_matrix_gpu, vol_stdev_matrix)
    cuda.memcpy_htod(IR_TickersID_List_matrix_gpu, IR_TickersID_List_matrix)

      
    mod = SourceModule("""
      #include <cstdlib>

//     __device__ int add_trade( int *trade_result_count, int TRADE_RESULT_COLUMN_COUNT, float *trade_result, int long_short_flag, int ticker_id, int entry_time_id, float entry_price, int exit_time_id, float exit_price, int stop_time_id, float IR_ticker_volume_stdev_threshold, float Non_IR_ticker_volume_stdev_threshold, float IR_ticker_shock_stdev_threshold, float Non_IR_ticker_shock_stdev_threshold, float IR_ticker_shock_count_threshold, float Non_IR_ticker_shock_count_threshold, float stop_loss_size_to_shock_ratio, float floating_stoploss_movement, int MaxHoldingPeriodInStdUnit)
     __device__ int add_trade( int *trade_result_count, int TRADE_RESULT_COLUMN_COUNT, float *trade_result, int long_short_flag, int ticker_id, int entry_time_id, float entry_price, int exit_time_id, float exit_price, int stop_time_id, float IR_ticker_volume_stdev_threshold, float Non_IR_ticker_volume_stdev_threshold, float IR_ticker_shock_stdev_threshold, float Non_IR_ticker_shock_stdev_threshold, float IR_ticker_shock_count_threshold, float Non_IR_ticker_shock_count_threshold, float stop_loss_size_to_shock_ratio, float floating_stoploss_movement, int MaxHoldingPeriodInStdUnit, float ticker_return_mean, float ticker_return_stdev, float ticker_vol_mean, float ticker_vol_stdev)
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
                        trade_result[trade_result_index_offset + 6] = IR_ticker_volume_stdev_threshold;
                        trade_result[trade_result_index_offset + 7] = Non_IR_ticker_volume_stdev_threshold;
                        trade_result[trade_result_index_offset + 8] = IR_ticker_shock_stdev_threshold;
                        trade_result[trade_result_index_offset + 9] = Non_IR_ticker_shock_stdev_threshold;
                        trade_result[trade_result_index_offset + 10] = IR_ticker_shock_count_threshold;
                        trade_result[trade_result_index_offset + 11] = Non_IR_ticker_shock_count_threshold;
                        trade_result[trade_result_index_offset + 12] = stop_loss_size_to_shock_ratio;
                        trade_result[trade_result_index_offset + 13] = floating_stoploss_movement;
                        trade_result[trade_result_index_offset + 14] = MaxHoldingPeriodInStdUnit;
                        trade_result[trade_result_index_offset + 15] = stop_time_id;
                        trade_result[trade_result_index_offset + 16] = ticker_return_mean;
                        trade_result[trade_result_index_offset + 17] = ticker_return_stdev;
                        trade_result[trade_result_index_offset + 18] = ticker_vol_mean;
                        trade_result[trade_result_index_offset + 19] = ticker_vol_stdev;
                    return 0;
      }
        
      __device__ int check_if_IR_Ticker( int ticker_id_to_check, int *IR_TickersID_List_matrix, int IR_TickersID_List_count)
        {
                  for (int check_ticker_id = 0; check_ticker_id < IR_TickersID_List_count; check_ticker_id++) {
                    if (IR_TickersID_List_matrix[check_ticker_id] == ticker_id_to_check) {
                      return 1;
                    }
                  }
                  return 0;
      }

      __device__ int check_if_general_market_shock( int time_id, int ticker_id_count, float IR_ticker_volume_stdev_threshold, float Non_IR_ticker_volume_stdev_threshold, float IR_ticker_shock_stdev_threshold, float Non_IR_ticker_shock_stdev_threshold, int IR_ticker_shock_count_threshold, int Non_IR_ticker_shock_count_threshold, int IR_TickersID_List_count, int *IR_TickersID_List_matrix, float *return_mean_matrix, float *return_stdev_matrix, float *vol_mean_matrix, float *vol_stdev_matrix, float *close_data, float *volume_data)
        {
            int IR_Ticker_shock_count, Non_IR_Ticker_shock_count, is_IR_ticker;
            float price_diff, price_diff_threshold, volume_threshold;
            IR_Ticker_shock_count = 0;
            Non_IR_Ticker_shock_count = 0;
            for (int ticker_id = 0; ticker_id < ticker_id_count; ticker_id++) {
//              price_diff = close_data[time_id * ticker_id_count + ticker_id] - close_data[(time_id - 1) * ticker_id_count + ticker_id];
              price_diff = (close_data[time_id * ticker_id_count + ticker_id] - close_data[(time_id - 1) * ticker_id_count + ticker_id]) / close_data[(time_id - 1) * ticker_id_count + ticker_id];
              is_IR_ticker = check_if_IR_Ticker( ticker_id, IR_TickersID_List_matrix, IR_TickersID_List_count);
              if (is_IR_ticker == 1) {
                price_diff_threshold = return_mean_matrix[ticker_id] + IR_ticker_shock_stdev_threshold * return_stdev_matrix[ticker_id];
                volume_threshold = vol_mean_matrix[ticker_id] + IR_ticker_volume_stdev_threshold * vol_stdev_matrix[ticker_id];
                if (abs(price_diff) > price_diff_threshold && volume_data[time_id * ticker_id_count + ticker_id] > volume_threshold) {
                  IR_Ticker_shock_count++;
                }
              } else {
                price_diff_threshold = return_mean_matrix[ticker_id] + Non_IR_ticker_shock_stdev_threshold * return_stdev_matrix[ticker_id];
                volume_threshold = vol_mean_matrix[ticker_id] + Non_IR_ticker_volume_stdev_threshold * vol_stdev_matrix[ticker_id];
                if (abs(price_diff) > price_diff_threshold && volume_data[time_id * ticker_id_count + ticker_id] > volume_threshold) {
                  Non_IR_Ticker_shock_count++;
                }
              }
            }
            if (IR_Ticker_shock_count >= IR_ticker_shock_count_threshold && Non_IR_Ticker_shock_count >= Non_IR_ticker_shock_count_threshold) {
              return 1;
            }
            return 0;
      }

//       __global__ void market_shock_analysis(int block_cutting_by_time, int second_dimension_size, int GPU_CORE_BLOCK_SIZE, int gpu_core_block_count, int first_dimension_size, int scenario_count, int scenario_column_count, int StartTimeInStdUnit, int EndTimeInStdUnit, int MaxHoldingPeriodInStdUnit, int IR_TickersID_List_count, int ErrorCode, int TRADE_RESULT_COLUMN_COUNT, int InitialResultCacheSize, int *trade_result_count, float *close_data, float *volume_data, float *date_id_data, float *time_std_unit_data, float *scenario_matrix, float *return_mean_matrix, float *return_stdev_matrix, float *vol_mean_matrix, float *vol_stdev_matrix, int *IR_TickersID_List_matrix, float *trade_result)
      __global__ void market_shock_analysis(int block_cutting_by_time, int second_dimension_size, int GPU_CORE_BLOCK_SIZE, int gpu_core_block_count, int first_dimension_size, int scenario_count, int scenario_column_count, int StartTimeInStdUnit, int EndTimeInStdUnit, int IR_TickersID_List_count, int ErrorCode, int TRADE_RESULT_COLUMN_COUNT, int InitialResultCacheSize, int *trade_result_count, float *close_data, float *volume_data, float *date_id_data, float *time_std_unit_data, float *scenario_matrix, float *return_mean_matrix, float *return_stdev_matrix, float *vol_mean_matrix, float *vol_stdev_matrix, int *IR_TickersID_List_matrix, float *trade_result)
      {
        int IR_ticker_shock_count_threshold, Non_IR_ticker_shock_count_threshold, scenario_id, scenario_id_offset, ticker_id, long_short_flag, entry_time_id, exit_time_id, stop_time_id, is_IR_ticker, is_general_market_shock, trade_end_time_id, MaxHoldingPeriodInStdUnit;
        float entry_price, exit_price, IR_ticker_volume_stdev_threshold, Non_IR_ticker_volume_stdev_threshold, IR_ticker_shock_stdev_threshold, Non_IR_ticker_shock_stdev_threshold, stop_loss_size_to_shock_ratio, floating_stoploss_movement, price_diff, price_diff_threshold, volume_threshold, stop_loss_price;
        ErrorCode = 0;

          for (int k = 0; k < gpu_core_block_count; k++) {
            scenario_id = k * GPU_CORE_BLOCK_SIZE + threadIdx.y;
            if (scenario_id < scenario_count) {
              scenario_id_offset = scenario_id * scenario_column_count;
              ticker_id = (int) scenario_matrix[scenario_id_offset];
              IR_ticker_volume_stdev_threshold = scenario_matrix[scenario_id_offset + 1];
              Non_IR_ticker_volume_stdev_threshold = scenario_matrix[scenario_id_offset + 2];
              IR_ticker_shock_stdev_threshold = scenario_matrix[scenario_id_offset + 3];
              Non_IR_ticker_shock_stdev_threshold = scenario_matrix[scenario_id_offset + 4];
              IR_ticker_shock_count_threshold = (int) scenario_matrix[scenario_id_offset + 5];
              Non_IR_ticker_shock_count_threshold = (int) scenario_matrix[scenario_id_offset + 6];
              stop_loss_size_to_shock_ratio = scenario_matrix[scenario_id_offset + 7];
              floating_stoploss_movement = scenario_matrix[scenario_id_offset + 8];
              MaxHoldingPeriodInStdUnit = scenario_matrix[scenario_id_offset + 9];
              
              long_short_flag = 0;
              entry_time_id = 0;
              entry_price = 0;
              exit_time_id = 0;
              exit_price = 0;
              stop_time_id = 0;
//              add_trade( trade_result_count, TRADE_RESULT_COLUMN_COUNT, trade_result, long_short_flag, ticker_id, entry_time_id, entry_price, exit_time_id, exit_price, stop_time_id, IR_ticker_volume_stdev_threshold, Non_IR_ticker_volume_stdev_threshold, IR_ticker_shock_stdev_threshold, Non_IR_ticker_shock_stdev_threshold, IR_ticker_shock_count_threshold, Non_IR_ticker_shock_count_threshold, stop_loss_size_to_shock_ratio, floating_stoploss_movement, MaxHoldingPeriodInStdUnit);

              for (int time_id = 1; time_id < first_dimension_size; time_id++) {
                if (time_std_unit_data[time_id] - time_std_unit_data[time_id-1] == 1) {
//                  price_diff = close_data[time_id * second_dimension_size + ticker_id] - close_data[(time_id - 1) * second_dimension_size + ticker_id];
                  price_diff = (close_data[time_id * second_dimension_size + ticker_id] - close_data[(time_id - 1) * second_dimension_size + ticker_id]) / close_data[(time_id - 1) * second_dimension_size + ticker_id];

                  is_IR_ticker = check_if_IR_Ticker( ticker_id, IR_TickersID_List_matrix, IR_TickersID_List_count);

                  for (int check_ticker_id = 0; check_ticker_id < IR_TickersID_List_count; check_ticker_id++) {
                    if (IR_TickersID_List_matrix[check_ticker_id] == ticker_id) {
                      is_IR_ticker = 1;
                    }
                  }

                  if (is_IR_ticker == 1) {
                    price_diff_threshold = return_mean_matrix[ticker_id] + IR_ticker_shock_stdev_threshold * return_stdev_matrix[ticker_id];
                    volume_threshold = vol_mean_matrix[ticker_id] + IR_ticker_volume_stdev_threshold * vol_stdev_matrix[ticker_id];
                  } else {
                    price_diff_threshold = return_mean_matrix[ticker_id] + Non_IR_ticker_shock_stdev_threshold * return_stdev_matrix[ticker_id];
                    volume_threshold = vol_mean_matrix[ticker_id] + Non_IR_ticker_volume_stdev_threshold * vol_stdev_matrix[ticker_id];
                  }

                  if (abs(price_diff) > price_diff_threshold && volume_data[time_id * second_dimension_size + ticker_id] > volume_threshold) {
                    is_general_market_shock = check_if_general_market_shock( time_id, second_dimension_size, IR_ticker_volume_stdev_threshold, Non_IR_ticker_volume_stdev_threshold, IR_ticker_shock_stdev_threshold, Non_IR_ticker_shock_stdev_threshold, IR_ticker_shock_count_threshold, Non_IR_ticker_shock_count_threshold, IR_TickersID_List_count, IR_TickersID_List_matrix, return_mean_matrix, return_stdev_matrix, vol_mean_matrix, vol_stdev_matrix, close_data, volume_data);
                    if (is_general_market_shock == 1) {
                      entry_time_id = time_id;
                      entry_price = close_data[time_id * second_dimension_size + ticker_id];
                      if (price_diff >= 0) {
                        long_short_flag = 1;
                      } else {
                        long_short_flag = -1;
                      }
//                      stop_loss_price = close_data[time_id * second_dimension_size + ticker_id] - price_diff * stop_loss_size_to_shock_ratio;
//                      stop_loss_price = close_data[time_id * second_dimension_size + ticker_id] * (1 + (price_diff * stop_loss_size_to_shock_ratio));
                      stop_loss_price = close_data[time_id * second_dimension_size + ticker_id] - (close_data[time_id * second_dimension_size + ticker_id] - close_data[(time_id - 1) * second_dimension_size + ticker_id]) * stop_loss_size_to_shock_ratio;
                      exit_time_id = 0;
                      
                      trade_end_time_id = time_id + MaxHoldingPeriodInStdUnit;
                      if (trade_end_time_id >= first_dimension_size ) {
                        trade_end_time_id = first_dimension_size - 1;
                      }
                      
                      for (int trade_time_id = time_id + 1; trade_time_id <= trade_end_time_id; trade_time_id++) {

                        if (time_std_unit_data[trade_time_id + 1] - time_std_unit_data[trade_time_id] == 1) {
                      
                      
                      
                          if (long_short_flag * close_data[trade_time_id * second_dimension_size + ticker_id] < long_short_flag * stop_loss_price) {
                            exit_time_id = trade_time_id;
                            stop_time_id = trade_time_id;
                            exit_price = close_data[trade_time_id * second_dimension_size + ticker_id];
//                            add_trade( trade_result_count, TRADE_RESULT_COLUMN_COUNT, trade_result, long_short_flag, ticker_id, entry_time_id, entry_price, exit_time_id, exit_price, stop_time_id, IR_ticker_volume_stdev_threshold, Non_IR_ticker_volume_stdev_threshold, IR_ticker_shock_stdev_threshold, Non_IR_ticker_shock_stdev_threshold, IR_ticker_shock_count_threshold, Non_IR_ticker_shock_count_threshold, stop_loss_size_to_shock_ratio, floating_stoploss_movement, MaxHoldingPeriodInStdUnit);
                            add_trade( trade_result_count, TRADE_RESULT_COLUMN_COUNT, trade_result, long_short_flag, ticker_id, entry_time_id, entry_price, exit_time_id, exit_price, stop_time_id, IR_ticker_volume_stdev_threshold, Non_IR_ticker_volume_stdev_threshold, IR_ticker_shock_stdev_threshold, Non_IR_ticker_shock_stdev_threshold, IR_ticker_shock_count_threshold, Non_IR_ticker_shock_count_threshold, stop_loss_size_to_shock_ratio, floating_stoploss_movement, MaxHoldingPeriodInStdUnit, return_mean_matrix[ticker_id], return_stdev_matrix[ticker_id], vol_mean_matrix[ticker_id], vol_stdev_matrix[ticker_id]);
                            long_short_flag = 0;
                            break;
                          } else {
                            if (long_short_flag > 0) {
                              stop_loss_price = stop_loss_price * (1 + floating_stoploss_movement);
                            } else {
                              stop_loss_price = stop_loss_price * (1 - floating_stoploss_movement);
                            }
                          }
                          
                        } else {
                          exit_time_id = trade_time_id;
                          stop_time_id = trade_time_id;
                          exit_price = close_data[trade_time_id * second_dimension_size + ticker_id];
//                          add_trade( trade_result_count, TRADE_RESULT_COLUMN_COUNT, trade_result, long_short_flag, ticker_id, entry_time_id, entry_price, exit_time_id, exit_price, stop_time_id, IR_ticker_volume_stdev_threshold, Non_IR_ticker_volume_stdev_threshold, IR_ticker_shock_stdev_threshold, Non_IR_ticker_shock_stdev_threshold, IR_ticker_shock_count_threshold, Non_IR_ticker_shock_count_threshold, stop_loss_size_to_shock_ratio, floating_stoploss_movement, MaxHoldingPeriodInStdUnit);
                          add_trade( trade_result_count, TRADE_RESULT_COLUMN_COUNT, trade_result, long_short_flag, ticker_id, entry_time_id, entry_price, exit_time_id, exit_price, stop_time_id, IR_ticker_volume_stdev_threshold, Non_IR_ticker_volume_stdev_threshold, IR_ticker_shock_stdev_threshold, Non_IR_ticker_shock_stdev_threshold, IR_ticker_shock_count_threshold, Non_IR_ticker_shock_count_threshold, stop_loss_size_to_shock_ratio, floating_stoploss_movement, MaxHoldingPeriodInStdUnit, return_mean_matrix[ticker_id], return_stdev_matrix[ticker_id], vol_mean_matrix[ticker_id], vol_stdev_matrix[ticker_id]);
                          long_short_flag = 0;
                          break;

                        }
                          
                      }
                      if (exit_time_id == 0) {
                          exit_time_id = trade_end_time_id;
                          stop_time_id = trade_end_time_id;
                          exit_price = close_data[trade_end_time_id * second_dimension_size + ticker_id];
//                          add_trade( trade_result_count, TRADE_RESULT_COLUMN_COUNT, trade_result, long_short_flag, ticker_id, entry_time_id, entry_price, exit_time_id, exit_price, stop_time_id, IR_ticker_volume_stdev_threshold, Non_IR_ticker_volume_stdev_threshold, IR_ticker_shock_stdev_threshold, Non_IR_ticker_shock_stdev_threshold, IR_ticker_shock_count_threshold, Non_IR_ticker_shock_count_threshold, stop_loss_size_to_shock_ratio, floating_stoploss_movement, MaxHoldingPeriodInStdUnit);
                          add_trade( trade_result_count, TRADE_RESULT_COLUMN_COUNT, trade_result, long_short_flag, ticker_id, entry_time_id, entry_price, exit_time_id, exit_price, stop_time_id, IR_ticker_volume_stdev_threshold, Non_IR_ticker_volume_stdev_threshold, IR_ticker_shock_stdev_threshold, Non_IR_ticker_shock_stdev_threshold, IR_ticker_shock_count_threshold, Non_IR_ticker_shock_count_threshold, stop_loss_size_to_shock_ratio, floating_stoploss_movement, MaxHoldingPeriodInStdUnit, return_mean_matrix[ticker_id], return_stdev_matrix[ticker_id], vol_mean_matrix[ticker_id], vol_stdev_matrix[ticker_id]);
                          long_short_flag = 0;
                          time_id = trade_end_time_id + 1;
                      }
                    }
                  }
                }  
              }
            }
          }
      }
      """)

    func = mod.get_function("market_shock_analysis")
    # func(np.int32(block_cutting_by_time), np.int32(second_dimension_size), np.int32(GPU_CORE_BLOCK_SIZE), np.int32(gpu_core_block_count), np.int32(first_dimension_size), np.int32(scenario_count), np.int32(scenario_column_count), np.int32(StartTimeInStdUnit), np.int32(EndTimeInStdUnit), np.int32(MaxHoldingPeriodInStdUnit), np.int32(IR_TickersID_List_count), np.int32(ErrorCode), np.int32(TRADE_RESULT_COLUMN_COUNT), np.int32(InitialResultCacheSize), trade_result_count_gpu, close_price_matrix_gpu, volume_matrix_gpu, date_id_matrix_gpu, time_std_unit_matrix_gpu, scenario_matrix_gpu, return_mean_matrix_gpu, return_stdev_matrix_gpu, vol_mean_matrix_gpu, vol_stdev_matrix_gpu, IR_TickersID_List_matrix_gpu, trade_result_gpu, block=(1,GPU_CORE_BLOCK_SIZE,1))
    func(np.int32(block_cutting_by_time), np.int32(second_dimension_size), np.int32(GPU_CORE_BLOCK_SIZE), np.int32(gpu_core_block_count), np.int32(first_dimension_size), np.int32(scenario_count), np.int32(scenario_column_count), np.int32(StartTimeInStdUnit), np.int32(EndTimeInStdUnit), np.int32(IR_TickersID_List_count), np.int32(ErrorCode), np.int32(TRADE_RESULT_COLUMN_COUNT), np.int32(InitialResultCacheSize), trade_result_count_gpu, close_price_matrix_gpu, volume_matrix_gpu, date_id_matrix_gpu, time_std_unit_matrix_gpu, scenario_matrix_gpu, return_mean_matrix_gpu, return_stdev_matrix_gpu, vol_mean_matrix_gpu, vol_stdev_matrix_gpu, IR_TickersID_List_matrix_gpu, trade_result_gpu, block=(1,GPU_CORE_BLOCK_SIZE,1))

    trade_result_count_out = np.empty_like(trade_result_count)
    cuda.memcpy_dtoh(trade_result_count_out, trade_result_count_gpu)
    trade_record = np.empty_like(trade_result)
    cuda.memcpy_dtoh(trade_record, trade_result_gpu)
    
    trade_result_gpu.free()
    close_price_matrix_gpu.free()
    date_id_matrix_gpu.free()
    trade_result_count_gpu.free()
    time_std_unit_matrix_gpu.free()
    
    # return pd.DataFrame(data=trade_record[0:trade_result_count_out], columns=TRADE_RESULT_COLUMNS)
    df = pd.DataFrame(data=trade_record[0:trade_result_count_out], columns=TRADE_RESULT_COLUMNS)
    print('trade record is')
    print(df)
    return df


