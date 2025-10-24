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
from datetime import date, datetime, timedelta
import InvestmentAnalytics.Config as Config
import numpy as np

# GPU_CORE_BLOCK_SIZE = 32*32
GPU_CORE_TOTAL_THREAD_SIZE = Config.CONFIG_CUDA_ThreadCount

def drop_duplicates(df, columns=None):
    import vaex
    """Return a :class:`DataFrame` object with no duplicates in the given columns.
    .. warning:: The resulting dataframe will be in memory, use with caution.
    :param columns: Column or list of column to remove duplicates by, default to all columns.
    :return: :class:`DataFrame` object with duplicates filtered away.
    """
    if columns is None:
        columns = df.get_column_names()
    if type(columns) is str:
        columns = [columns]
    return df.groupby(columns, agg={'__hidden_count': vaex.agg.count()}).drop('__hidden_count')

def CUDATradeIDAssignment(scenario_identifier, number_of_segment_key_column, Debug = False):
    print('Start CUDATradeIDAssignment with number_of_segment_key_column = ' + str(number_of_segment_key_column) + ' at ' + str(datetime.now()))
    print('If error please try to increase TradeIDSortingSegmentKeyColumnsCount')
    
    # all_column_names = scenario_identifier.columns.values.tolist()
    if Debug:
        OutputColumnCount = 14
    else:
        OutputColumnCount = 1

    trade_id_all = np.empty((0, OutputColumnCount), int)
    
    # print('number_of_segment_key_column is ' + str(number_of_segment_key_column))
    
    if number_of_segment_key_column > 0:
        segment_key_column_names = scenario_identifier.columns[:number_of_segment_key_column].values.tolist()
        
        # print('segment_key_column_names is ' + str(segment_key_column_names))
        
        SegmentID = 0
        segment_detail_column_names = scenario_identifier.columns.values.tolist()
        for column_name in segment_key_column_names:
            segment_detail_column_names.remove(column_name)
        segment_unique_keys = scenario_identifier[segment_key_column_names].drop_duplicates()
        
        for index, row in segment_unique_keys.iterrows():
            scenario_identifier_in_segment = scenario_identifier.copy()
            for column_name in segment_key_column_names:
                scenario_identifier_in_segment = scenario_identifier_in_segment.loc[scenario_identifier_in_segment[column_name] == row[column_name]].copy()
                
            trade_id = CUDATradeIDAssignmentOnOneSegment(scenario_identifier_in_segment, segment_detail_column_names, OutputColumnCount, SegmentID)
            
            trade_id_all = np.append(trade_id_all, trade_id, axis=0)
            SegmentID = SegmentID + 1
    else:
        scenario_identifier_in_segment = scenario_identifier.copy()
        trade_id_all = CUDATradeIDAssignmentOnOneSegment(scenario_identifier_in_segment, scenario_identifier.columns.values.tolist(), OutputColumnCount, 0)
        
    if Debug:
        # trade_id_all = pd.DataFrame(trade_id_all,  columns=["trade id", "thread id", "block pointer", "start block pointer", "next block pointer", "entry TimeInStandardUnit this block", "entry TimeInStandardUnit prior block", "exit TimeInStandardUnit this block", "exit TimeInStandardUnit prior block", "Segment ID", "a1", "a2", "a3", "a4"])
        trade_id_all = pd.DataFrame(trade_id_all,  columns=["trade id", "thread id", "block pointer", "start block pointer", "next block pointer", "entry TimeInStandardUnit this block", "entry TimeInStandardUnit prior block", "exit TimeInStandardUnit this block", "exit TimeInStandardUnit prior block", "Segment ID", "first_dimension_size", "GPU_CORE_TOTAL_THREAD_SIZE", "size_of_each_block", "a4"])
    else:
        trade_id_all = pd.DataFrame(trade_id_all,  columns=["trade id"])
    
    return trade_id_all

def CUDATradeIDAssignmentOnOneSegment(scenario_identifier_in_segment, segment_detail_column_names, OutputColumnCount, SegmentID):
    # print('Start of CUDATradeIDAssignmentOnOneSegment at ' + str(datetime.now()))

    GPU_CORE_BLOCK_SIZE = min(1024,GPU_CORE_TOTAL_THREAD_SIZE)
    GPU_CORE_GRID_SIZE = math.ceil(GPU_CORE_TOTAL_THREAD_SIZE / 1024)
    # print('GPU_CORE_TOTAL_THREAD_SIZE is ' + str(GPU_CORE_TOTAL_THREAD_SIZE) + 'GPU_CORE_BLOCK_SIZE is ' + str(GPU_CORE_BLOCK_SIZE) + ', GPU_CORE_GRID_SIZE is ' + str(GPU_CORE_GRID_SIZE))

    scenario_identifier_in_segment = scenario_identifier_in_segment[segment_detail_column_names]
    if isinstance(scenario_identifier_in_segment, pd.DataFrame):
        scenario_identifier_matrix = scenario_identifier_in_segment.to_numpy()
    else:
        # import dask.dataframe as dd
        # import dask.array as da
        # import dask.bag as db
        scenario_identifier_matrix = scenario_identifier_in_segment.compute().to_numpy()
        

    ErrorCode = 0
    first_dimension_size = len(scenario_identifier_matrix)
    second_dimension_size = len(segment_detail_column_names)
    # print('first_dimension_size is ' + str(first_dimension_size) + ' and second_dimension_size is ' + str(second_dimension_size))
    gpu_core_block_count = math.ceil(first_dimension_size/GPU_CORE_TOTAL_THREAD_SIZE)
    pending_zeros = np.zeros((GPU_CORE_TOTAL_THREAD_SIZE*gpu_core_block_count - first_dimension_size, second_dimension_size))
    
    scenario_identifier_matrix = np.concatenate((scenario_identifier_matrix, pending_zeros)).astype(np.float32).copy(order="C")
    trade_id_matrix = np.zeros((GPU_CORE_TOTAL_THREAD_SIZE*gpu_core_block_count,OutputColumnCount)).astype(np.int32)
    scenario_identifier_matrix_gpu = cuda.mem_alloc(scenario_identifier_matrix.nbytes)
    trade_id_matrix_gpu = cuda.mem_alloc(trade_id_matrix.nbytes)
    cuda.memcpy_htod(scenario_identifier_matrix_gpu, scenario_identifier_matrix)
    cuda.memcpy_htod(trade_id_matrix_gpu, trade_id_matrix)
    
    mod = SourceModule("""
      __global__ void trade_id_assign(int second_dimension_size, int gpu_core_block_count, int first_dimension_size, int OutputColumnCount, int SegmentID, int ErrorCode, float *scenario_identifier_matrix, int *trade_id)
      {
        int GPU_CORE_TOTAL_THREAD_SIZE, k, block_start_pointer, next_block_start_pointer, block_row_offset, trade_id_index, prior_trade_id_index, size_of_each_block;
        bool same_scenario, can_quit_when_next_scenario, can_start_assigning;
        const int trade_id_of_last_trade = 0;
        
        GPU_CORE_TOTAL_THREAD_SIZE = blockDim.x * gridDim.x;
        
        size_of_each_block = (int) ((first_dimension_size / GPU_CORE_TOTAL_THREAD_SIZE) + 1);
        
        k = blockIdx.x * blockDim.x + threadIdx.x;
//        k = threadIdx.y;

        block_start_pointer = k * size_of_each_block;
        next_block_start_pointer = (k+1) * size_of_each_block;
        can_start_assigning = false;
        
        if (block_start_pointer == 0) {
          trade_id[0] = trade_id_of_last_trade;
          
          if (OutputColumnCount > 1) {
            trade_id[1] = k;
            trade_id[2] = 0;
            trade_id[3] = block_start_pointer;
            trade_id[4] = next_block_start_pointer;
            trade_id[5] = scenario_identifier_matrix[0];
            trade_id[6] = scenario_identifier_matrix[0];
            trade_id[7] = scenario_identifier_matrix[1];
            trade_id[8] = scenario_identifier_matrix[1];
            trade_id[9] = SegmentID;
            trade_id[10] = first_dimension_size;
            trade_id[11] = GPU_CORE_TOTAL_THREAD_SIZE;
            trade_id[12] = size_of_each_block;
          }
          can_start_assigning = true;
          block_start_pointer = 1;
        }
        
        can_quit_when_next_scenario = false;
        for (int p = block_start_pointer; p < first_dimension_size; p++) {
          trade_id_index = p * OutputColumnCount;
          prior_trade_id_index = (p - 1) * OutputColumnCount;
          
          if (p > next_block_start_pointer) {
            can_quit_when_next_scenario = true;
          }
          same_scenario = true;
          block_row_offset = p * second_dimension_size;
          
          for (int i = 0; i < second_dimension_size; i++) {
            if (scenario_identifier_matrix[block_row_offset + i] != scenario_identifier_matrix[block_row_offset + i - second_dimension_size]) {
              same_scenario = false;
            }
          }
          
          if (same_scenario) {
            if (can_start_assigning) {
              trade_id[trade_id_index] = trade_id[prior_trade_id_index] + 1;
                  
              if (OutputColumnCount > 1) {
                trade_id[trade_id_index + 1] = k;
                trade_id[trade_id_index + 2] = p;
                trade_id[trade_id_index + 3] = block_start_pointer;
                trade_id[trade_id_index + 4] = next_block_start_pointer;
                trade_id[trade_id_index + 5] = scenario_identifier_matrix[block_row_offset + 2];
                trade_id[trade_id_index + 6] = scenario_identifier_matrix[block_row_offset + 2 - second_dimension_size];
                trade_id[trade_id_index + 7] = scenario_identifier_matrix[block_row_offset + 3];
                trade_id[trade_id_index + 8] = scenario_identifier_matrix[block_row_offset + 3 - second_dimension_size];
                trade_id[trade_id_index + 9] = SegmentID;
                trade_id[trade_id_index + 10] = first_dimension_size;
                trade_id[trade_id_index + 11] = GPU_CORE_TOTAL_THREAD_SIZE;
                trade_id[trade_id_index + 12] = size_of_each_block;
//                trade_id[trade_id_index + 13] = scenario_identifier_matrix[3];
              }
              
            }
         // assigning trade id for next scenario
          } else {
                  
           trade_id[trade_id_index] = trade_id_of_last_trade;
                
            if (OutputColumnCount > 1) {
              trade_id[trade_id_index + 1] = k;
              trade_id[trade_id_index + 2] = p;
              trade_id[trade_id_index + 3] = block_start_pointer;
              trade_id[trade_id_index + 4] = next_block_start_pointer;
              trade_id[trade_id_index + 5] = scenario_identifier_matrix[block_row_offset + 2];
              trade_id[trade_id_index + 6] = scenario_identifier_matrix[block_row_offset + 2 - second_dimension_size];
              trade_id[trade_id_index + 7] = scenario_identifier_matrix[block_row_offset + 3];
              trade_id[trade_id_index + 8] = scenario_identifier_matrix[block_row_offset + 3 - second_dimension_size];
              trade_id[trade_id_index + 9] = SegmentID;
              trade_id[trade_id_index + 10] = first_dimension_size;
              trade_id[trade_id_index + 11] = GPU_CORE_TOTAL_THREAD_SIZE;
              trade_id[trade_id_index + 12] = size_of_each_block;
//              trade_id[trade_id_index + 13] = scenario_identifier_matrix[3];
            }

            can_start_assigning = true;
            if (can_quit_when_next_scenario) {
              if (OutputColumnCount > 1) {
                trade_id[trade_id_index + 13] = p;
              }
              p = first_dimension_size;
            }
          }
        }
      }
      """)
          
    func = mod.get_function("trade_id_assign")
    func(np.int32(second_dimension_size), np.int32(gpu_core_block_count), np.int32(first_dimension_size), np.int32(OutputColumnCount), np.int32(SegmentID), np.int32(ErrorCode),  scenario_identifier_matrix_gpu, trade_id_matrix_gpu, block=(GPU_CORE_BLOCK_SIZE,1,1), grid=(GPU_CORE_GRID_SIZE, 1))

    trade_id = np.empty_like(trade_id_matrix)
    cuda.memcpy_dtoh(trade_id, trade_id_matrix_gpu)
    
    scenario_identifier_matrix_gpu.free()
    trade_id_matrix_gpu.free()

    # print('Finish of CUDATradeIDAssignmentOnOneSegment at ' + str(datetime.now()))
    return trade_id[0:first_dimension_size]


# def CUDATradeIDAssignmentVaex(scenario_identifier, number_of_segment_key_column, Debug = False):
#     print('Start CUDATradeIDAssignmentVaex with number_of_segment_key_column = ' + str(number_of_segment_key_column) + ' at ' + str(datetime.now()))
    
#     import vaex
#     # all_column_names = scenario_identifier.columns.values.tolist()
#     if Debug:
#         OutputColumnCount = 14
#     else:
#         OutputColumnCount = 1

#     trade_id_all = np.empty((0, OutputColumnCount), int)
    
#     # print('number_of_segment_key_column is ' + str(number_of_segment_key_column))
    
#     if number_of_segment_key_column > 0:
#         # segment_key_column_names = scenario_identifier.columns[:number_of_segment_key_column].values.tolist()
#         segment_key_column_names = scenario_identifier.get_column_names()[:number_of_segment_key_column]
#         # print('segment_key_column_names is ' + str(segment_key_column_names))
#         SegmentID = 0
#         # segment_detail_column_names = scenario_identifier.columns.values.tolist()
#         segment_detail_column_names = scenario_identifier.get_column_names()
#         for column_name in segment_key_column_names:
#             segment_detail_column_names.remove(column_name)
#         # segment_unique_keys = scenario_identifier[segment_key_column_names].drop_duplicates()
#         segment_unique_keys = drop_duplicates(scenario_identifier[segment_key_column_names])
#         for index, row in segment_unique_keys.iterrows():
#             scenario_identifier_in_segment = scenario_identifier.copy()
#             for column_name in segment_key_column_names:
#                 # scenario_identifier_in_segment = scenario_identifier_in_segment.loc[scenario_identifier_in_segment[column_name] == row[column_name]].copy()
#                 scenario_identifier_in_segment = scenario_identifier_in_segment[scenario_identifier_in_segment[column_name] == row[column_name]].copy()
                
#             # print('scenario_identifier_in_segment is')
#             # print(scenario_identifier_in_segment)
#             # print('segment_detail_column_names is')
#             # print(segment_detail_column_names)
                
#             trade_id = CUDATradeIDAssignmentOnOneSegmentVaex(scenario_identifier_in_segment, segment_detail_column_names, OutputColumnCount, SegmentID)
            
#             trade_id_all = np.append(trade_id_all, trade_id, axis=0)
#             SegmentID = SegmentID + 1
#     else:
#         scenario_identifier_in_segment = scenario_identifier.copy()
#         trade_id_all = CUDATradeIDAssignmentOnOneSegmentVaex(scenario_identifier_in_segment, scenario_identifier.columns.values.tolist(), OutputColumnCount, 0)
        
#     if Debug:
#         trade_id_all = pd.DataFrame(trade_id_all,  columns=["trade id", "thread id", "block pointer", "start block pointer", "next block pointer", "entry TimeInStandardUnit this block", "entry TimeInStandardUnit prior block", "exit TimeInStandardUnit this block", "exit TimeInStandardUnit prior block", "Segment ID", "a1", "a2", "a3", "a4"])
#     else:
#         trade_id_all = pd.DataFrame(trade_id_all,  columns=["trade id"])
    
#     return vaex.from_pandas(df=trade_id_all, copy_index=False)

# def CUDATradeIDAssignmentOnOneSegmentVaex(scenario_identifier_in_segment, segment_detail_column_names, OutputColumnCount, SegmentID):
#     scenario_identifier_in_segment = scenario_identifier_in_segment[segment_detail_column_names]
#     # scenario_identifier_matrix = scenario_identifier_in_segment.to_numpy()
#     print('before vaex to numpy at ' + str(datetime.now()))
#     dictionary = scenario_identifier_in_segment.to_dict()
#     scenario_identifier_matrix = np.array([dictionary[key] for key in segment_detail_column_names]).T
#     print('after vaex to numpy at ' + str(datetime.now()))

#     ErrorCode = 0
#     first_dimension_size = len(scenario_identifier_matrix)
#     second_dimension_size = len(segment_detail_column_names)
#     # print('first_dimension_size is ' + str(first_dimension_size) + ' and second_dimension_size is ' + str(second_dimension_size))
#     gpu_core_block_count = math.ceil(first_dimension_size/GPU_CORE_BLOCK_SIZE)
#     pending_zeros = np.zeros((GPU_CORE_BLOCK_SIZE*gpu_core_block_count - first_dimension_size, second_dimension_size))
    
#     scenario_identifier_matrix = np.concatenate((scenario_identifier_matrix, pending_zeros)).astype(np.float32).copy(order="C")
#     trade_id_matrix = np.zeros((GPU_CORE_BLOCK_SIZE*gpu_core_block_count,OutputColumnCount)).astype(np.int32)
#     # a = a.astype(np.float32)
#     # a = a.copy(order="C")
#     # a_out = a_out.astype(np.int32)
#     scenario_identifier_matrix_gpu = cuda.mem_alloc(scenario_identifier_matrix.nbytes)
#     trade_id_matrix_gpu = cuda.mem_alloc(trade_id_matrix.nbytes)
#     cuda.memcpy_htod(scenario_identifier_matrix_gpu, scenario_identifier_matrix)
#     cuda.memcpy_htod(trade_id_matrix_gpu, trade_id_matrix)
    
#     mod = SourceModule("""
#       __global__ void trade_id_assign(int second_dimension_size, int GPU_CORE_BLOCK_SIZE, int gpu_core_block_count, int first_dimension_size, int OutputColumnCount, int SegmentID, int ErrorCode, float *scenario_identifier_matrix, int *trade_id)
#       {
#         int k, block_start_pointer, next_block_start_pointer, block_row_offset, trade_id_index, prior_trade_id_index;
#         bool same_scenario, can_quit_when_next_scenario, can_start_assigning;
#         const int trade_id_of_last_trade = 0;
#           k = threadIdx.y;
#             block_start_pointer = (int) k * first_dimension_size / GPU_CORE_BLOCK_SIZE;
#             next_block_start_pointer = (int) (k+1) * first_dimension_size / GPU_CORE_BLOCK_SIZE;
#             can_start_assigning = false;
#             if (block_start_pointer == 0) {
#               trade_id[0] = trade_id_of_last_trade;
#               if (OutputColumnCount > 1) {
#                 trade_id[1] = k;
#                 trade_id[2] = 0;
#                 trade_id[3] = block_start_pointer;
#                 trade_id[4] = next_block_start_pointer;
#                 trade_id[5] = scenario_identifier_matrix[0];
#                 trade_id[6] = scenario_identifier_matrix[0];
#                 trade_id[7] = scenario_identifier_matrix[1];
#                 trade_id[8] = scenario_identifier_matrix[1];
#                 trade_id[9] = SegmentID;
#               }
#               can_start_assigning = true;
#               block_start_pointer = 1;
#             }
#             can_quit_when_next_scenario = false;
#             for (int p = block_start_pointer; p < first_dimension_size; p++) {
#               trade_id_index = p * OutputColumnCount;
#               prior_trade_id_index = (p - 1) * OutputColumnCount;
#               if (p > next_block_start_pointer) {
#                 can_quit_when_next_scenario = true;
#               }
#               same_scenario = true;
#               block_row_offset = p * second_dimension_size;
#               for (int i = 0; i < second_dimension_size; i++) {
#                 if (scenario_identifier_matrix[block_row_offset + i] != scenario_identifier_matrix[block_row_offset + i - second_dimension_size]) {
#                   same_scenario = false;
#                 }
#               }
#               if (same_scenario) {
#                 if (can_start_assigning) {
#                   trade_id[trade_id_index] = trade_id[prior_trade_id_index] + 1;
#                   if (OutputColumnCount > 1) {
#                     trade_id[trade_id_index + 1] = k;
#                     trade_id[trade_id_index + 2] = p;
#                     trade_id[trade_id_index + 3] = block_start_pointer;
#                     trade_id[trade_id_index + 4] = next_block_start_pointer;
#                     trade_id[trade_id_index + 5] = scenario_identifier_matrix[block_row_offset + 2];
#                     trade_id[trade_id_index + 6] = scenario_identifier_matrix[block_row_offset + 2 - second_dimension_size];
#                     trade_id[trade_id_index + 7] = scenario_identifier_matrix[block_row_offset + 3];
#                     trade_id[trade_id_index + 8] = scenario_identifier_matrix[block_row_offset + 3 - second_dimension_size];
#                     trade_id[trade_id_index + 9] = SegmentID;
#                     trade_id[trade_id_index + 10] = scenario_identifier_matrix[0];
#                     trade_id[trade_id_index + 11] = scenario_identifier_matrix[1];
#                     trade_id[trade_id_index + 12] = scenario_identifier_matrix[2];
#                     trade_id[trade_id_index + 13] = scenario_identifier_matrix[3];
#                   }
#                 }
#               } else {
#                 trade_id[trade_id_index] = trade_id_of_last_trade;
#                 if (OutputColumnCount > 1) {
#                   trade_id[trade_id_index + 1] = k;
#                   trade_id[trade_id_index + 2] = p;
#                   trade_id[trade_id_index + 3] = block_start_pointer;
#                   trade_id[trade_id_index + 4] = next_block_start_pointer;
#                   trade_id[trade_id_index + 5] = scenario_identifier_matrix[block_row_offset + 2];
#                   trade_id[trade_id_index + 6] = scenario_identifier_matrix[block_row_offset + 2 - second_dimension_size];
#                   trade_id[trade_id_index + 7] = scenario_identifier_matrix[block_row_offset + 3];
#                   trade_id[trade_id_index + 8] = scenario_identifier_matrix[block_row_offset + 3 - second_dimension_size];
#                   trade_id[trade_id_index + 9] = SegmentID;
#                     trade_id[trade_id_index + 10] = scenario_identifier_matrix[0];
#                     trade_id[trade_id_index + 11] = scenario_identifier_matrix[1];
#                     trade_id[trade_id_index + 12] = scenario_identifier_matrix[2];
#                     trade_id[trade_id_index + 13] = scenario_identifier_matrix[3];
#                 }
#                 can_start_assigning = true;
#                 if (can_quit_when_next_scenario) {
#                   p = first_dimension_size;
#                 }
#               }
#             }
#       }
#       """)
          
#     func = mod.get_function("trade_id_assign")
#     func(np.int32(second_dimension_size), np.int32(GPU_CORE_BLOCK_SIZE), np.int32(gpu_core_block_count), np.int32(first_dimension_size), np.int32(OutputColumnCount), np.int32(SegmentID), np.int32(ErrorCode),  scenario_identifier_matrix_gpu, trade_id_matrix_gpu, block=(1,GPU_CORE_BLOCK_SIZE,1))

#     trade_id = np.empty_like(trade_id_matrix)
#     cuda.memcpy_dtoh(trade_id, trade_id_matrix_gpu)
    
#     scenario_identifier_matrix_gpu.free()
#     trade_id_matrix_gpu.free()

#     return trade_id[0:first_dimension_size]


    