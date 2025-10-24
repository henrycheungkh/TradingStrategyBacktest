# -*- coding: utf-8 -*-
"""
Created on Thu Jul 29 14:15:19 2021

@author: Henry Cheung
"""

from datetime import date, datetime, timedelta
import pycuda.driver as cuda
import pycuda.autoinit
from pycuda.compiler import SourceModule
import math
import pandas as pd
import scipy.stats
import InvestmentAnalytics.CUDA.CUDAPathSetting
import InvestmentAnalytics.Config as Config

import numpy as np

# GPU_CORE_BLOCK_SIZE = 32*32
GPU_CORE_TOTAL_THREAD_SIZE = Config.CONFIG_CUDA_ThreadCount
GPU_CORE_BLOCK_SIZE = min(1024,GPU_CORE_TOTAL_THREAD_SIZE)
GPU_CORE_GRID_SIZE = math.ceil(GPU_CORE_TOTAL_THREAD_SIZE / 1024)

def CUDABacktestingSummary(long_short_flag_matrix, entry_price_matrix, exit_price_matrix, BacktestTradeCountLabel, GeneratePnlMatrix = False):
    
# =IF(A2=0;"";A2*(H2-F2))
# =AVERAGE(V2:V53)
# =IF(A2=0;"";(V2-$V$1)^2)   
# =SQRT(AVERAGE(W2:W53))
    
    STANDARD_BACKTEST_RESULT_COLUMNS = ['number of trades', 'average return per trade', 'stdev of point return per trade', 'max drawdown', 'max drawup', 'win percentage', 'long ratio', 't-score']
    BACKTEST_SUMMARY_COLUMN_COUNT = len(STANDARD_BACKTEST_RESULT_COLUMNS)
    ErrorCode = 0
    
    BacktestPeriodCount = len(BacktestTradeCountLabel)
    BacktestPeriod = list(BacktestTradeCountLabel)
    BacktestPeriodArray = np.asarray(BacktestPeriod)
    
    scenario_size = len(long_short_flag_matrix)
    trade_id_size = len(long_short_flag_matrix[0])
    print('in CUDABacktestingSummary, scenario_size = ' + str(scenario_size) + ' and trade_id_size = ' + str(trade_id_size) + ' at ' + str(datetime.now()))
    # print('long_short_flag_matrix is')
    # print(long_short_flag_matrix)
    
    BacktestPeriodArray[0] = trade_id_size
    BacktestPeriodArray = BacktestPeriodArray.astype(np.int32)
    
    # gpu_core_block_count = math.ceil(scenario_size/GPU_CORE_BLOCK_SIZE)
    gpu_core_block_count = math.ceil(scenario_size/(GPU_CORE_BLOCK_SIZE * GPU_CORE_GRID_SIZE))


    print('long_short_flag_matrix is with dimension ' + str(len(long_short_flag_matrix)) + ' x ' + str(len(long_short_flag_matrix[0])))
    
    backtest_summary_out = np.zeros((scenario_size * BacktestPeriodCount, BACKTEST_SUMMARY_COLUMN_COUNT)).astype(np.float32)
    #number of trades, average return per trade, stdev of point return per trade, max drawdown, max drawup, win percentage, long ratio, t-score, p-value
    if GeneratePnlMatrix:
        pnl_matrix = np.zeros((scenario_size, trade_id_size)).astype(np.float32)
        generate_pnl_matrix_flag = 1
    else:
        pnl_matrix = np.zeros((1, trade_id_size)).astype(np.float32)
        generate_pnl_matrix_flag = 0
    
    long_short_flag_matrix_gpu = cuda.mem_alloc(long_short_flag_matrix.nbytes)
    entry_price_matrix_gpu = cuda.mem_alloc(entry_price_matrix.nbytes)
    exit_price_matrix_gpu = cuda.mem_alloc(exit_price_matrix.nbytes)
    BacktestPeriodArray_gpu = cuda.mem_alloc(BacktestPeriodArray.nbytes)
    backtest_summary_out_gpu = cuda.mem_alloc(backtest_summary_out.nbytes)
    pnl_matrix_gpu = cuda.mem_alloc(pnl_matrix.nbytes)
    
    cuda.memcpy_htod(long_short_flag_matrix_gpu, long_short_flag_matrix)
    cuda.memcpy_htod(entry_price_matrix_gpu, entry_price_matrix)
    cuda.memcpy_htod(exit_price_matrix_gpu, exit_price_matrix)
    cuda.memcpy_htod(BacktestPeriodArray_gpu, BacktestPeriodArray)
    cuda.memcpy_htod(backtest_summary_out_gpu, backtest_summary_out)
    cuda.memcpy_htod(pnl_matrix_gpu, pnl_matrix)
      
    mod = SourceModule("""
      #include <cmath> 
    
        __global__ void backtest_summary(int trade_id_size, int gpu_core_block_count, int scenario_size, int backtest_period_count, int BACKTEST_SUMMARY_COLUMN_COUNT, int generate_pnl_matrix_flag, int ErrorCode, int *long_short_flag, float *entry_price, float *exit_price, int *end_trade_id, float *backtest_summary, float *pnl_matrix)
        {
          ErrorCode = 0;
          int thread_Index, GPU_CORE_BLOCK_SIZE, x, data_index_offset, backtest_summary_offset;
          float point_pnl, prior_accumul_pnl_high, prior_accumul_pnl_low, accumul_pnl;
          
          GPU_CORE_BLOCK_SIZE = blockDim.x * gridDim.x;
          thread_Index = blockIdx.x * blockDim.x + threadIdx.x;

            for (int k = 0; k < gpu_core_block_count; k++) {
              x = k * GPU_CORE_BLOCK_SIZE + thread_Index;
              if (x < scenario_size) {
                for (int backtest_period_index = 0; backtest_period_index < backtest_period_count; backtest_period_index++) {
                  backtest_summary_offset = (backtest_period_index * scenario_size + x) * BACKTEST_SUMMARY_COLUMN_COUNT;
                  prior_accumul_pnl_high = 0;
                  prior_accumul_pnl_low = 0;
                  accumul_pnl = 0;
                  for (int y = 0; y < end_trade_id[backtest_period_index]; y++) {
                    data_index_offset = x * trade_id_size + y;
                    if (abs(long_short_flag[data_index_offset]) != 0) {
                      point_pnl = long_short_flag[data_index_offset] * (exit_price[data_index_offset] - entry_price[data_index_offset]);
                      accumul_pnl = accumul_pnl + point_pnl;
                      if (accumul_pnl > prior_accumul_pnl_high) {
                        prior_accumul_pnl_high = accumul_pnl;
                      }
                      if (accumul_pnl - prior_accumul_pnl_high < backtest_summary[backtest_summary_offset + 3]) {
                        backtest_summary[backtest_summary_offset + 3] = accumul_pnl - prior_accumul_pnl_high;
                      }
                      if (accumul_pnl < prior_accumul_pnl_low) {
                        prior_accumul_pnl_low = accumul_pnl;
                      }
                      if (accumul_pnl - prior_accumul_pnl_low > backtest_summary[backtest_summary_offset + 4]) {
                        backtest_summary[backtest_summary_offset + 4] = accumul_pnl - prior_accumul_pnl_low;
                      }
                      backtest_summary[backtest_summary_offset] = backtest_summary[backtest_summary_offset] + abs(long_short_flag[data_index_offset]);
                      if (long_short_flag[data_index_offset] > 0) {
                        backtest_summary[backtest_summary_offset + 6] = backtest_summary[backtest_summary_offset + 6] + long_short_flag[data_index_offset];
                      }
                      backtest_summary[backtest_summary_offset + 1] = backtest_summary[backtest_summary_offset + 1] + point_pnl;
                      if (point_pnl > 0) {
                        backtest_summary[backtest_summary_offset + 5] = backtest_summary[backtest_summary_offset + 5] + abs(long_short_flag[data_index_offset]);
                      }
                    }
                  }
//                  backtest_summary[backtest_summary_offset + 7] = backtest_summary[backtest_summary_offset + 1];
                  if(backtest_summary[backtest_summary_offset] > 0) {
                    backtest_summary[backtest_summary_offset + 1] = backtest_summary[backtest_summary_offset + 1] / backtest_summary[backtest_summary_offset];
                    backtest_summary[backtest_summary_offset + 5] = backtest_summary[backtest_summary_offset + 5] / backtest_summary[backtest_summary_offset];
                    backtest_summary[backtest_summary_offset + 6] = backtest_summary[backtest_summary_offset + 6] / backtest_summary[backtest_summary_offset];
                  }

                  backtest_summary[backtest_summary_offset + 2] = 0;
                  backtest_summary[backtest_summary_offset + 7] = 0;
                  backtest_summary[backtest_summary_offset + 7] = end_trade_id[backtest_period_index];
                  for (int y = 0; y < end_trade_id[backtest_period_index]; y++) {
                    data_index_offset = x * trade_id_size + y;
                    if (abs(long_short_flag[data_index_offset]) != 0) {
                      backtest_summary[backtest_summary_offset + 2] = backtest_summary[backtest_summary_offset + 2] + pow((long_short_flag[data_index_offset] * (exit_price[data_index_offset] - entry_price[data_index_offset])) - backtest_summary[backtest_summary_offset + 1], 2);
                    }
                  }
                  if(backtest_summary[backtest_summary_offset] > 0) {
                    backtest_summary[backtest_summary_offset + 2] = pow(backtest_summary[backtest_summary_offset + 2] / backtest_summary[backtest_summary_offset], 0.5);
                  }

                  if (backtest_summary[backtest_summary_offset] >= 3) {
                    backtest_summary[backtest_summary_offset + 7] = backtest_summary[backtest_summary_offset + 1] * pow(backtest_summary[backtest_summary_offset], 0.5) / backtest_summary[backtest_summary_offset + 2];
                  }
                  //number of trades, average return per trade, stdev of point return per trade, max drawdown, max drawup, win percentage, long ratio, t-score
                }
              }
            }
        }
      """)      
    
    func = mod.get_function("backtest_summary")
    func(np.int32(trade_id_size), np.int32(gpu_core_block_count), np.int32(scenario_size), np.int32(BacktestPeriodCount), np.int32(BACKTEST_SUMMARY_COLUMN_COUNT), np.int32(generate_pnl_matrix_flag), np.int32(ErrorCode), long_short_flag_matrix_gpu, entry_price_matrix_gpu, exit_price_matrix_gpu, BacktestPeriodArray_gpu, backtest_summary_out_gpu, pnl_matrix_gpu, block=(GPU_CORE_BLOCK_SIZE,1,1), grid=(GPU_CORE_GRID_SIZE, 1))
    
    backtest_summary = np.empty_like(backtest_summary_out)
    cuda.memcpy_dtoh(backtest_summary, backtest_summary_out_gpu)
    
    backtest_summary_df = pd.DataFrame()
    
    for BacktestPeriodIndex in range(BacktestPeriodCount):
        backtest_summary_subset = backtest_summary[BacktestPeriodIndex*scenario_size:(BacktestPeriodIndex+1)*scenario_size]
        backtest_summary_subset_df = pd.DataFrame(data=backtest_summary_subset, columns=STANDARD_BACKTEST_RESULT_COLUMNS)
        backtest_summary_subset_df['p-value'] = scipy.stats.t.sf(abs(backtest_summary_subset_df['t-score']), df=backtest_summary_subset_df['number of trades'] - 1)
        backtest_summary_subset_df['p-value-z-score'] = scipy.stats.norm.sf(abs(backtest_summary_subset_df['average return per trade']/backtest_summary_subset_df['stdev of point return per trade']))
        backtest_summary_subset_df['scenario id'] = backtest_summary_subset_df.index
        backtest_summary_subset_df['backtest period'] = BacktestTradeCountLabel[BacktestPeriod[BacktestPeriodIndex]]
        # backtest_summary_df = backtest_summary_df.append(backtest_summary_subset_df)
        backtest_summary_df = pd.concat([backtest_summary_df, backtest_summary_subset_df])
#number of trades, average return per trade, stdev of point return per trade, max drawdown, win percentage, long ratio

    if GeneratePnlMatrix:
        pnl_matrix = np.empty_like(pnl_matrix)
        cuda.memcpy_dtoh(pnl_matrix, pnl_matrix_gpu)
    else:
        pnl_matrix = None
    
    backtest_summary_out_gpu.free()
    pnl_matrix_gpu.free()
    long_short_flag_matrix_gpu.free()
    entry_price_matrix_gpu.free()
    exit_price_matrix_gpu.free()
    BacktestPeriodArray_gpu.free()
    
    return backtest_summary_df, pnl_matrix


def CUDABacktestingRapidCalibrationSummary(long_short_flag_matrix, entry_price_matrix, exit_price_matrix, date_id_matrix, BacktestTradeCountLabel, TimeIDMapping, Scenario_IDMapping, RapidCalibrationTopScenarioSelectedCount, RapidCalibrationFrequencyTag):
    STANDARD_BACKTEST_RESULT_COLUMNS = ['ticker id', 'calib trade obs count', 'number of trades', 'average return per trade', 'stdev of point return per trade', 'max drawdown', 'max drawup', 'win percentage', 'long ratio', 't-score']
    BACKTEST_SUMMARY_COLUMN_COUNT = len(STANDARD_BACKTEST_RESULT_COLUMNS)
    RAPID_CALIBRATION_TRADE_RECORD_COLUMNS = ['long short flag', 'ticker id', 'calib trade obs count', 'date id', 'scenario id', 'entry price', 'exit price']
    RAPID_CALIBRATION_TRADE_RECORD_COLUMN_COUNT = len(RAPID_CALIBRATION_TRADE_RECORD_COLUMNS)
    
    BacktestPeriod = list(BacktestTradeCountLabel)
    BacktestPeriod.remove(0)
    # print('BacktestPeriod is')
    # print(BacktestPeriod)
    BacktestPeriodMax = max(BacktestPeriod)
    BacktestPeriodArray = np.asarray(BacktestPeriod)
    BacktestPeriodArray = BacktestPeriodArray.astype(np.int32)
    
    
    # print('BacktestTradeCountLabel in dict before cutting is')
    # print(BacktestTradeCountLabel)
    BacktestTradeCountLabel = list(BacktestTradeCountLabel.keys())
    # print('BacktestTradeCountLabel in list before cutting is')
    # print(BacktestTradeCountLabel)
    # BacktestTradeCountLabel = BacktestTradeCountLabel[1:len(BacktestTradeCountLabel)-1]
    # del BacktestTradeCountLabel[0]
    BacktestTradeCountLabel.remove(0)
    # print('BacktestTradeCountLabel after cutting is')
    # print(BacktestTradeCountLabel)
    BacktestPeriodCount = len(BacktestTradeCountLabel)
    scenario_size = len(long_short_flag_matrix)
    trade_id_size = len(long_short_flag_matrix[0])
    # print('in CUDABacktestingRapidCalibrationSummary, TimdIDMapping is')
    # print(TimeIDMapping)
    # print('in CUDABacktestingRapidCalibrationSummary, Scenario_IDMapping is')
    # print(Scenario_IDMapping)
    scenario_id_detail_matrix = Scenario_IDMapping.to_numpy().copy(order="C")
    # print('scenario_id_detail_matrix is with dimension ' + str(len(scenario_id_detail_matrix)) + ' x ' + str(len(scenario_id_detail_matrix[0])))
    # print(scenario_id_detail_matrix)

    
    date_id_list = TimeIDMapping[['date id']].drop_duplicates()
    ticker_id_list = Scenario_IDMapping[['ticker id']].drop_duplicates()
    
    date_id_size = len(date_id_list)
    ticker_id_size = len(ticker_id_list)
    
    # gpu_core_block_count = math.ceil(scenario_size/GPU_CORE_BLOCK_SIZE)
    gpu_core_block_count = math.ceil(scenario_size/(GPU_CORE_BLOCK_SIZE * GPU_CORE_GRID_SIZE))

    sharpe_ratio_matrix = np.zeros((BacktestPeriodCount * scenario_size, date_id_size))
    g = np.zeros(BacktestPeriodMax)
    ErrorCode = np.zeros(1).astype(np.int32)

    long_short_flag_gpu = cuda.mem_alloc(long_short_flag_matrix.nbytes)
    entry_price_gpu = cuda.mem_alloc(entry_price_matrix.nbytes)
    exit_price_gpu = cuda.mem_alloc(exit_price_matrix.nbytes)
    date_id_gpu = cuda.mem_alloc(date_id_matrix.nbytes)
    
    # print('long_short_flag_matrix is with dimension ' + str(len(long_short_flag_matrix)) + ' x ' + str(len(long_short_flag_matrix[0])))
    # print(long_short_flag_matrix.dtype)
    # print(long_short_flag_matrix)
    # print('entry_price_matrix is with dimension ' + str(len(entry_price_matrix)) + ' x ' + str(len(entry_price_matrix[0])))
    # print(entry_price_matrix.dtype)
    # print('exit_price_matrix is with dimension ' + str(len(exit_price_matrix)) + ' x ' + str(len(exit_price_matrix[0])))
    # print(exit_price_matrix.dtype)
    # print('date_id_matrix is with dimension ' + str(len(date_id_matrix)) + ' x ' + str(len(date_id_matrix[0])))
    # print(date_id_matrix.dtype)
    # print(date_id_matrix)
    
    sharpe_ratio_gpu = cuda.mem_alloc(sharpe_ratio_matrix.nbytes)
    g_gpu = cuda.mem_alloc(g.nbytes)
    
    trade_obs_count_gpu = cuda.mem_alloc(BacktestPeriodArray.nbytes)
    ErrorCode_gpu = cuda.mem_alloc(ErrorCode.nbytes)
    
    cuda.memcpy_htod(long_short_flag_gpu, long_short_flag_matrix)
    cuda.memcpy_htod(entry_price_gpu, entry_price_matrix)
    cuda.memcpy_htod(exit_price_gpu, exit_price_matrix)
    cuda.memcpy_htod(date_id_gpu, date_id_matrix)
    cuda.memcpy_htod(sharpe_ratio_gpu, sharpe_ratio_matrix)
    cuda.memcpy_htod(trade_obs_count_gpu, BacktestPeriodArray)
    cuda.memcpy_htod(g_gpu, g)
    cuda.memcpy_htod(ErrorCode_gpu, ErrorCode)

    mod = SourceModule("""
      #include <cmath> 
    
        __global__ void backtest_rapid_calibration_sharpe_ratio(int trade_id_size, int gpu_core_block_count, int scenario_size, int backtest_period_count, int max_backtest_period, int BACKTEST_SUMMARY_COLUMN_COUNT, int date_id_count, int ticker_id_count, int ErrorCode, int *long_short_flag, float *entry_price, float *exit_price, int *date_id, float *sharpe_ratio, int *trade_obs_count, float *out_pnl)
//    func(np.int32(trade_id_size), np.int32(GPU_CORE_BLOCK_SIZE), np.int32(gpu_core_block_count), np.int32(scenario_size), np.int32(BacktestPeriodCount), np.int32(BACKTEST_SUMMARY_COLUMN_COUNT), np.int32(date_id_size), np.int32(ticker_id_size), ErrorCode_gpu, long_short_flag_gpu, entry_price_gpu, exit_price_gpu, date_id_gpu, sharpe_ratio_gpu, trade_obs_count_gpu, g_gpu, block=(1,GPU_CORE_BLOCK_SIZE,1))
        {
          int thread_Index, GPU_CORE_BLOCK_SIZE, trade_obs_count_index, scenario_index, next_date_id_to_scan, input_data_index, found_trade_id_count, trade_id_of_trade_before_date;
          float mean, stdev;
          float *pnl = new float[max_backtest_period];
          
          GPU_CORE_BLOCK_SIZE = blockDim.x * gridDim.x;
          thread_Index = blockIdx.x * blockDim.x + threadIdx.x;

          for (int gpu_core_block_index = 0; gpu_core_block_index < gpu_core_block_count; gpu_core_block_index++) {
            scenario_index = gpu_core_block_index * GPU_CORE_BLOCK_SIZE + thread_Index;
            if (scenario_index < scenario_size) {
            
              for (int trade_obs_count_index = 0; trade_obs_count_index<backtest_period_count; trade_obs_count_index++) {
                next_date_id_to_scan = 0;
                for (int date_id_index = 0; date_id_index < date_id_count; date_id_index++) {
                  if (date_id_index >= next_date_id_to_scan) {

                    for (int trade_id_index = trade_id_size-1; trade_id_index >= 0; trade_id_index--) {
                      input_data_index = scenario_index * trade_id_size + trade_id_index;
                      if (date_id[input_data_index] <  date_id_index) {
                      trade_id_of_trade_before_date = trade_id_index;
                        break;
                      }
                    }
                      
                    found_trade_id_count = 0;
                    for (int obs_trade_id_index = trade_id_of_trade_before_date; obs_trade_id_index > 0  ; obs_trade_id_index-- ) {
                      input_data_index = scenario_index * trade_id_size + obs_trade_id_index;
                      if (long_short_flag[input_data_index] != 0) {
                        pnl[found_trade_id_count] = long_short_flag[input_data_index] * (exit_price[input_data_index] - entry_price[input_data_index]);
                        found_trade_id_count++;
                        if (found_trade_id_count >= trade_obs_count[trade_obs_count_index]) {
                          break;
                        }
                      }
                    }

                    mean = 0;
                    stdev = 0;
                    if (found_trade_id_count >= trade_obs_count[trade_obs_count_index]) {
                      for (int i = 0; i<found_trade_id_count; i++) {
                        mean = mean + pnl[i];
                      }
                      mean = mean / found_trade_id_count;
                      for (int i = 0; i<found_trade_id_count; i++) {
                        stdev = stdev + pow(pnl[i] - mean, 2);
                      }
                      stdev = pow(stdev / found_trade_id_count, 0.5);
                      if (stdev == 0) {
                        stdev = 100000;
                      }
                    }
                    if (input_data_index < date_id_count) {
                      if (date_id[input_data_index+1] > 0) {
                        next_date_id_to_scan = date_id[input_data_index+1] + 1;
                      }
                    }
                  }
                  sharpe_ratio[(trade_obs_count_index * scenario_size + scenario_index) * date_id_count + date_id_index] = mean / stdev;
                }
              }
            }
          }
          delete *pnl;

        }
      """)      
    
    func = mod.get_function("backtest_rapid_calibration_sharpe_ratio")
    func(np.int32(trade_id_size), np.int32(gpu_core_block_count), np.int32(scenario_size), np.int32(BacktestPeriodCount), np.int32(BacktestPeriodMax), np.int32(BACKTEST_SUMMARY_COLUMN_COUNT), np.int32(date_id_size), np.int32(ticker_id_size), ErrorCode_gpu, long_short_flag_gpu, entry_price_gpu, exit_price_gpu, date_id_gpu, sharpe_ratio_gpu, trade_obs_count_gpu, g_gpu, block=(GPU_CORE_BLOCK_SIZE,1,1), grid=(GPU_CORE_GRID_SIZE, 1))
    
    print('backtest_rapid_calibration_sharpe_ratio finished running at ' + str(datetime.now()))

    sharpe_ratio_matrix = np.empty_like(sharpe_ratio_matrix)
    cuda.memcpy_dtoh(sharpe_ratio_matrix, sharpe_ratio_gpu)
    Error_Code = np.empty_like(ErrorCode)
    cuda.memcpy_dtoh(Error_Code, ErrorCode_gpu)
    # print('Sharpe_Ratio is')
    # print(sharpe_ratio_matrix)
    # print('Error_Code[0] is')
    # print(Error_Code[0])

    a_out = np.zeros((BacktestPeriodCount * ticker_id_size * date_id_size * RapidCalibrationTopScenarioSelectedCount, RAPID_CALIBRATION_TRADE_RECORD_COLUMN_COUNT))
    a_out_gpu = cuda.mem_alloc(a_out.nbytes)
    cuda.memcpy_htod(a_out_gpu, a_out)
    trade_result_count = np.int32(0)
    b_out_gpu = cuda.mem_alloc(trade_result_count.nbytes)
    cuda.memcpy_htod(b_out_gpu, trade_result_count)
    
    scenario_id_detail_gpu = cuda.mem_alloc(scenario_id_detail_matrix.nbytes)
    cuda.memcpy_htod(scenario_id_detail_gpu, scenario_id_detail_matrix)

    # gpu_core_block_count = math.ceil(date_id_size * ticker_id_size/GPU_CORE_BLOCK_SIZE)
    gpu_core_block_count = math.ceil(date_id_size * ticker_id_size/(GPU_CORE_BLOCK_SIZE * GPU_CORE_GRID_SIZE))

    mod2 = SourceModule("""
      #include <cmath> 
    
        __global__ void backtest_rapid_calibration_trade_record(int trade_id_size, int gpu_core_block_count, int scenario_size, int backtest_period_count, int RAPID_CALIBRATION_TRADE_RECORD_COLUMN_COUNT, int date_id_count, int ticker_id_count, int rapid_calibration_top_scenario_selected_count, int ErrorCode, int *long_short_flag, float *entry_price, float *exit_price, int *date_id, float *sharpe_ratio, int *trade_obs_count, float *pnl_matrix, int *scenario_id_detail_matrix, float *trade_record, int *trade_result_count)
//    func(np.int32(trade_id_size), np.int32(GPU_CORE_BLOCK_SIZE), np.int32(gpu_core_block_count), np.int32(scenario_size), np.int32(BacktestPeriodCount), np.int32(RAPID_CALIBRATION_TRADE_RECORD_COLUMN_COUNT), np.int32(date_id_size), np.int32(ticker_id_size), np.int32(RapidCalibrationTopScenarioSelectedCount), np.int32(ErrorCode), long_short_flag_gpu, entry_price_gpu, exit_price_gpu, date_id_gpu, sharpe_ratio_gpu, trade_obs_count_gpu, g_gpu, scenario_id_detail_gpu, a_out_gpu, b_out_gpu, block=(1,GPU_CORE_BLOCK_SIZE,1))
        {
          const int scenario_detail_columns_count = 8;
          int thread_Index, GPU_CORE_BLOCK_SIZE, ticker_id, date_id_index, trade_result_index, trade_result_index_offset, obs_timeinstandardunit, entry_timein;
          float this_sharpe_ratio;
          float *max_sharpe_ratio_after_abs = new float[rapid_calibration_top_scenario_selected_count];
          int *max_abs_sharpe_ratio_scenario_id = new int[rapid_calibration_top_scenario_selected_count];
          
          GPU_CORE_BLOCK_SIZE = blockDim.x * gridDim.x;
          thread_Index = blockIdx.x * blockDim.x + threadIdx.x;

          for (int gpu_core_block_index = 0; gpu_core_block_index < gpu_core_block_count; gpu_core_block_index++) {
            ticker_id_date_index = gpu_core_block_index * GPU_CORE_BLOCK_SIZE + thread_Index;
            if (ticker_id_date_index < date_id_count * ticker_id_count) {
            
              ticker_id = (int) ticker_id_date_index / date_id_count;
              date_id_index = ticker_id_date_index % date_id_count;
              
              if (date_id_index > 0) {


              
                for (int trade_obs_count_index = 0; trade_obs_count_index<backtest_period_count; trade_obs_count_index++) {
              
                  for (int i=0; i<rapid_calibration_top_scenario_selected_count; i++) {
                    max_sharpe_ratio_after_abs[i] = 0;
                    max_abs_sharpe_ratio_scenario_id[i] = -1;
                  }
                  for (int scenario_id = 0; scenario_id < scenario_size; scenario_id++) {
                    if (scenario_id_detail_matrix[scenario_id * scenario_detail_columns_count] == ticker_id) {
                      this_sharpe_ratio = sharpe_ratio[(trade_obs_count_index * scenario_size + scenario_id) * date_id_count + date_id_index];
                      for (int i=rapid_calibration_top_scenario_selected_count-1; i>=0; i--) {
                        if (abs(this_sharpe_ratio) > abs(max_sharpe_ratio_after_abs[i])) {
                          for (int j=i+1; j<rapid_calibration_top_scenario_selected_count; j++) {
                            max_sharpe_ratio_after_abs[j] = max_sharpe_ratio_after_abs[j-1];
                            max_abs_sharpe_ratio_scenario_id[j] = max_abs_sharpe_ratio_scenario_id[j-1];
                          }
                          max_sharpe_ratio_after_abs[i] = this_sharpe_ratio;
                          max_abs_sharpe_ratio_scenario_id[i] = scenario_id;
                        }
                      }
                    }
                  }

                  for (int i=0; i<rapid_calibration_top_scenario_selected_count; i++) {
                    if (max_sharpe_ratio_after_abs[i] != 0) {
                      trade_result_index = atomicAdd(trade_result_count,1);
                      trade_result_index_offset = trade_result_index * RAPID_CALIBRATION_TRADE_RECORD_COLUMN_COUNT ;
                      if (max_sharpe_ratio_after_abs[i] > 0) {
                        //trade_result[trade_result_index_offset + 0] = 1;
                      } else {
                        //trade_result[trade_result_index_offset + 0] = -1;
                      }
                      trade_result[trade_result_index_offset + 1] = ticker_id;
                      trade_result[trade_result_index_offset + 2] = trade_obs_count[trade_obs_count_index];
                      trade_result[trade_result_index_offset + 3] = date_id_index;
                      trade_result[trade_result_index_offset + 4] = max_abs_sharpe_ratio_scenario_id[i];
                      trade_result[trade_result_index_offset + 5] = date_id_index;
                      trade_result[trade_result_index_offset + 6] = date_id_index;
                      
                  
  //    RAPID_CALIBRATION_TRADE_RECORD_COLUMNS = ['long short flag', 'ticker id', 'calib trade obs count', 'date id', 'scenario id', 'entry price', 'exit price']

                    }
                  }
                
                
                
                }
              }
                    
                    
                    


            }
            
          }
          
          delete *max_abs_sharpe_ratio;
          delete *max_abs_sharpe_ratio_scenario_id;
          
        }
      """)      

    func = mod2.get_function("backtest_rapid_calibration_trade_record")
    func(np.int32(trade_id_size), np.int32(gpu_core_block_count), np.int32(scenario_size), np.int32(BacktestPeriodCount), np.int32(RAPID_CALIBRATION_TRADE_RECORD_COLUMN_COUNT), np.int32(date_id_size), np.int32(ticker_id_size), np.int32(RapidCalibrationTopScenarioSelectedCount), np.int32(ErrorCode), long_short_flag_gpu, entry_price_gpu, exit_price_gpu, date_id_gpu, sharpe_ratio_gpu, trade_obs_count_gpu, g_gpu, scenario_id_detail_gpu, a_out_gpu, b_out_gpu, block=(GPU_CORE_BLOCK_SIZE,1,1), grid=(GPU_CORE_GRID_SIZE, 1))

    trade_record = np.empty_like(a_out)
    cuda.memcpy_dtoh(trade_record, a_out_gpu)

    print('backtest_rapid_calibration_trade_record finished running')
    
    raise Exception("Manual stopping")

    return None


