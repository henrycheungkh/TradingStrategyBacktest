# -*- coding: utf-8 -*-
"""
Created on Tue Sep 14 10:58:18 2021

@author: Henry Cheung
"""

import pycuda.driver as cuda
import pycuda.autoinit
from pycuda.compiler import SourceModule
import math
import pandas as pd
import InvestmentAnalytics.CUDA.CUDAPathSetting

import numpy as np

GPU_CORE_BLOCK_SIZE = 32*32
MAX_KEY_LEVEL_COUNT = 100000
MAX_WING_SIZE = 3*60
MIN_WING_SIZE = 5
PIVOT_AREA_PCT = 0.25


def CUDAIdentifyKeyLevelPivot(close_price_matrix, high_price_matrix, low_price_matrix, volume_matrix, minimum_slopes, first_consecutive_boundary_breach_tolerances, key_level_score_multiplier = [1, 1, 1, 1, 1], block_cutting_dimension = "Time Dimension"):
    IDENTIFIED_KEY_LEVELS_COLUMNS = ['ticker id', 'identified time id', 'key level price', 'pivot point down', 'observe high low price', 'minimum slope', 'first consecutive boundary breach tolerances', 'wing length', 'pivot area to wing volume ratio', 'pivot area to pre wing volume ratio', 'key level type specific score']
    # KEY_LEVELS_SCORE_MULTIPLIER = np.asarray([1, 1, 1, 1, 1]).astype(np.float32)
    KEY_LEVELS_SCORE_MULTIPLIER = np.asarray(key_level_score_multiplier).astype(np.float32)
    # observe high low price, slope, wing length, pivot area to wing volume ratio, pivot area to pre wing volume ratio
    IDENTIFIED_KEY_LEVELS_COLUMNS_COUNT = len(IDENTIFIED_KEY_LEVELS_COLUMNS)


    block_cutting_by_time = 0
    ErrorCode = 0
    if block_cutting_dimension == "Time Dimension":
        close_price_matrix = close_price_matrix.T.copy(order="C")
        high_price_matrix = high_price_matrix.T.copy(order="C")
        low_price_matrix = low_price_matrix.T.copy(order="C")
        volume_matrix = volume_matrix.T.copy(order="C")
        block_cutting_by_time = 1
        
    # print('close_price_matrix is with dimension ' + str(len(close_price_matrix)) + ' x ' + str(len(close_price_matrix[0])) )
    # print(close_price_matrix.flags)
    # print(close_price_matrix)
    
    first_dimension_size = len(close_price_matrix)
    second_dimension_size = len(close_price_matrix[0])

    gpu_core_block_count = math.ceil(first_dimension_size/GPU_CORE_BLOCK_SIZE)
    # print('gpu_core_block_count is ' + str(gpu_core_block_count))

    minimum_slopes_count = len(minimum_slopes)
    minimum_slopes_matrix = np.asarray(minimum_slopes).astype(np.float32)
    first_consecutive_boundary_breach_tolerances_count = len(first_consecutive_boundary_breach_tolerances)
    first_consecutive_boundary_breach_tolerances_matrix = np.asarray(first_consecutive_boundary_breach_tolerances).astype(np.int32)

    close_price_gpu = cuda.mem_alloc(close_price_matrix.nbytes)
    high_price_gpu = cuda.mem_alloc(high_price_matrix.nbytes)
    low_price_gpu = cuda.mem_alloc(low_price_matrix.nbytes)
    volume_gpu = cuda.mem_alloc(volume_matrix.nbytes)
    key_level_score_multiplier_gpu = cuda.mem_alloc(KEY_LEVELS_SCORE_MULTIPLIER.nbytes)
    minimum_slopes_gpu = cuda.mem_alloc(minimum_slopes_matrix.nbytes)
    first_consecutive_boundary_breach_tolerances_gpu = cuda.mem_alloc(first_consecutive_boundary_breach_tolerances_matrix.nbytes)
    
    cuda.memcpy_htod(close_price_gpu, close_price_matrix)
    cuda.memcpy_htod(high_price_gpu, high_price_matrix)
    cuda.memcpy_htod(low_price_gpu, low_price_matrix)
    cuda.memcpy_htod(volume_gpu, volume_matrix)
    cuda.memcpy_htod(key_level_score_multiplier_gpu, KEY_LEVELS_SCORE_MULTIPLIER)
    cuda.memcpy_htod(minimum_slopes_gpu, minimum_slopes_matrix)
    cuda.memcpy_htod(first_consecutive_boundary_breach_tolerances_gpu, first_consecutive_boundary_breach_tolerances_matrix)

    identified_key_level_count = np.int32(0)
    identified_key_level_count_gpu = cuda.mem_alloc(identified_key_level_count.nbytes)
    identified_key_levels = np.zeros((MAX_KEY_LEVEL_COUNT, IDENTIFIED_KEY_LEVELS_COLUMNS_COUNT)).astype(np.float32) #long short flag, ticker id, obs time id, entry time id, entry price, exit time id, exit price, trade id
    
    identified_key_levels_gpu = cuda.mem_alloc(identified_key_levels.nbytes)
    cuda.memcpy_htod(identified_key_levels_gpu, identified_key_levels)

    mod = SourceModule("""
                       
    #include <math.h>
    
      __device__ int ceil_reinvented( float f)
      {
        int i;
        i = (int) f;
        if (f > i) {
          return i + 1;
        } else {
          return i;
        }
      }
        
      __device__ int min_int( int in_integer1, int in_integer2)
      {
        if (in_integer1 < in_integer2) {
          return in_integer1;
        } else {
          return in_integer2;
        }
      }

      __device__ int check_pivot_wing( int wing_slope_sign, int wing_direction_sign, float *price_to_use, int ticker_size, int ticker_id, int time_id_size, int peak_scanning_time_id, int MAX_WING_SIZE, int first_consecutive_boundary_breach_tolerances, float minimum_slope)
      {
        int scanning_time_length, scanning_time_id_boundary, wing_length, tolerable_boundary_breach, peak_scanning_time_id_offset, scanning_time_id_offset;
        float slope, next_price_on_boundary;

        scanning_time_length = MAX_WING_SIZE;
        if (wing_direction_sign < 0 && peak_scanning_time_id - scanning_time_length < 0) {
          scanning_time_length = peak_scanning_time_id;
        }
        if (wing_direction_sign > 0 && peak_scanning_time_id + scanning_time_length >= time_id_size) {
          scanning_time_length = time_id_size - peak_scanning_time_id - 1;
        }
        wing_length = 0;
        slope = 1 + (minimum_slope * wing_slope_sign);
        tolerable_boundary_breach = first_consecutive_boundary_breach_tolerances;
        peak_scanning_time_id_offset = peak_scanning_time_id * ticker_size;
        next_price_on_boundary = price_to_use[peak_scanning_time_id_offset + ticker_id] * slope;
        for (int time_offset = 1; time_offset <= scanning_time_length; time_offset++) {
          scanning_time_id_offset = (peak_scanning_time_id + (time_offset * wing_direction_sign)) * ticker_size;
          if (wing_slope_sign * price_to_use[scanning_time_id_offset + ticker_id] < wing_slope_sign * next_price_on_boundary) {
            if (wing_slope_sign * price_to_use[scanning_time_id_offset + ticker_id] > wing_slope_sign * price_to_use[peak_scanning_time_id_offset + ticker_id] && tolerable_boundary_breach > 0) {
              tolerable_boundary_breach--;
            } else {
              break;
            }
          } else {
            if (tolerable_boundary_breach < first_consecutive_boundary_breach_tolerances) {
              wing_length = wing_length + (first_consecutive_boundary_breach_tolerances - tolerable_boundary_breach);
            }
            tolerable_boundary_breach = 0;
            wing_length++;
            next_price_on_boundary = next_price_on_boundary * slope;
          }
        }
        return wing_length;
      }

      __device__ int check_and_add_pivot( int MIN_WING_SIZE, int second_dimension_size, int *identified_key_level_count, float *identified_key_levels, int IDENTIFIED_KEY_LEVELS_COLUMNS_COUNT, int price_mode, int wing_slope_sign, float *close_data, int ticker_id, int time_id_size, int peak_scanning_time_id, int MAX_WING_SIZE, int first_consecutive_boundary_breach_tolerances, float minimum_slope, float *key_level_score_multiplier)
      {
        int wing_length, left_wing_length, right_wing_length, identified_key_level_index, identified_key_level_index_offset;
        
        left_wing_length = check_pivot_wing( 1, -1, close_data, second_dimension_size, ticker_id, time_id_size, peak_scanning_time_id, MAX_WING_SIZE, first_consecutive_boundary_breach_tolerances, minimum_slope);
        if (left_wing_length >= MIN_WING_SIZE) 
        {
          right_wing_length = check_pivot_wing( 1, 1, close_data, second_dimension_size, ticker_id, time_id_size, peak_scanning_time_id, MAX_WING_SIZE, first_consecutive_boundary_breach_tolerances, minimum_slope);
          if (right_wing_length >= MIN_WING_SIZE) 
          {
            wing_length = min_int(left_wing_length, right_wing_length);
            if (wing_length >= MIN_WING_SIZE) 
            {
              identified_key_level_index = atomicAdd(identified_key_level_count,1);
              identified_key_level_index_offset = identified_key_level_index * IDENTIFIED_KEY_LEVELS_COLUMNS_COUNT;
              identified_key_levels[identified_key_level_index_offset + 0] = ticker_id;
              identified_key_levels[identified_key_level_index_offset + 1] = peak_scanning_time_id;
              identified_key_levels[identified_key_level_index_offset + 2] = close_data[peak_scanning_time_id * second_dimension_size + ticker_id];
              identified_key_levels[identified_key_level_index_offset + 3] = 1;
              identified_key_levels[identified_key_level_index_offset + 4] = price_mode;
              identified_key_levels[identified_key_level_index_offset + 5] = minimum_slope;
              identified_key_levels[identified_key_level_index_offset + 6] = first_consecutive_boundary_breach_tolerances;
              identified_key_levels[identified_key_level_index_offset + 7] = wing_length;
              identified_key_levels[identified_key_level_index_offset + 8] = 1;
              identified_key_levels[identified_key_level_index_offset + 9] = 1;
              identified_key_levels[identified_key_level_index_offset + 10] = minimum_slope * key_level_score_multiplier[0] + wing_length * key_level_score_multiplier[1] + identified_key_levels[identified_key_level_index_offset + 8] * key_level_score_multiplier[2] + identified_key_levels[identified_key_level_index_offset + 9] * key_level_score_multiplier[3];
                            
//    IDENTIFIED_KEY_LEVELS_COLUMNS = ['ticker id', 'identified time id', 'key level price', 'pivot point down', 'observe high low price', 'minimum slope', 'first consecutive boundary breach tolerances', 'wing length', 'pivot area to wing volume ratio', 'pivot area to pre wing volume ratio', 'key level type specific score']
            }
          }
        }
        return 0;
      }

      __global__ void identify_key_level(int block_cutting_by_time, int second_dimension_size, int GPU_CORE_BLOCK_SIZE, int gpu_core_block_count, int first_dimension_size, int minimum_slopes_count, int first_consecutive_boundary_breach_tolerances_count, int IDENTIFIED_KEY_LEVELS_COLUMNS_COUNT, int MAX_WING_SIZE, int MIN_WING_SIZE, float pivot_area_pct, int ErrorCode, float *minimum_slopes, int *first_consecutive_boundary_breach_tolerances_matrix, float *close_data, float *high_data, float *low_data, float *volume_data, float *key_level_score_multiplier, int *identified_key_level_count, float *identified_key_levels)
      {
        int peak_scanning_time_id_start, peak_scanning_time_id_end, dummy;
        float *high_price_to_use, *low_price_to_use;

        if (block_cutting_by_time == 1) {
          for (int price_mode = 0; price_mode < 2; price_mode++) {
            for (int ticker_id = 0; ticker_id < second_dimension_size; ticker_id++) {
              for (int first_consecutive_boundary_breach_tolerances_index = 0; first_consecutive_boundary_breach_tolerances_index < first_consecutive_boundary_breach_tolerances_count; first_consecutive_boundary_breach_tolerances_index++) {
                for (int minimum_slopes_index = 0; minimum_slopes_index < minimum_slopes_count; minimum_slopes_index++) {
                  peak_scanning_time_id_start = ceil_reinvented(first_dimension_size * threadIdx.y / GPU_CORE_BLOCK_SIZE);
                  if (peak_scanning_time_id_start < first_dimension_size && peak_scanning_time_id_start > 0) 
                  {
                    peak_scanning_time_id_end = peak_scanning_time_id_start + GPU_CORE_BLOCK_SIZE;
                    if (peak_scanning_time_id_start < MIN_WING_SIZE) {
                      peak_scanning_time_id_start = MIN_WING_SIZE;
                    }
                    if (peak_scanning_time_id_end >= first_dimension_size - MIN_WING_SIZE) {
                      peak_scanning_time_id_end = first_dimension_size - MIN_WING_SIZE - 1;
                    }
                    for (int peak_scanning_time_id = peak_scanning_time_id_start; peak_scanning_time_id <= peak_scanning_time_id_end; peak_scanning_time_id++) {
                      if (price_mode == 0) {
                        high_price_to_use = close_data;
                        low_price_to_use = close_data;
                      } else {
                        high_price_to_use = high_data;
                        low_price_to_use = low_data;
                      }
                        
                      dummy = check_and_add_pivot( MIN_WING_SIZE, second_dimension_size, identified_key_level_count, identified_key_levels, IDENTIFIED_KEY_LEVELS_COLUMNS_COUNT, price_mode, 1, low_price_to_use, ticker_id, first_dimension_size, peak_scanning_time_id, MAX_WING_SIZE, first_consecutive_boundary_breach_tolerances_matrix[first_consecutive_boundary_breach_tolerances_index], minimum_slopes[minimum_slopes_index],  key_level_score_multiplier);
                      dummy = check_and_add_pivot( MIN_WING_SIZE, second_dimension_size, identified_key_level_count, identified_key_levels, IDENTIFIED_KEY_LEVELS_COLUMNS_COUNT, price_mode, -1, high_price_to_use, ticker_id, first_dimension_size, peak_scanning_time_id, MAX_WING_SIZE, first_consecutive_boundary_breach_tolerances_matrix[first_consecutive_boundary_breach_tolerances_index], minimum_slopes[minimum_slopes_index], key_level_score_multiplier);
                    }
                  }
                }
              } 
            } 
          }
        }
      }
      """)

    func = mod.get_function("identify_key_level")
    func(np.int32(block_cutting_by_time), np.int32(second_dimension_size), np.int32(GPU_CORE_BLOCK_SIZE), np.int32(gpu_core_block_count), np.int32(first_dimension_size), np.int32(minimum_slopes_count), np.int32(first_consecutive_boundary_breach_tolerances_count), np.int32(IDENTIFIED_KEY_LEVELS_COLUMNS_COUNT), np.int32(MAX_WING_SIZE), np.int32(MIN_WING_SIZE), np.float32(PIVOT_AREA_PCT), np.int32(ErrorCode), minimum_slopes_gpu, first_consecutive_boundary_breach_tolerances_gpu, close_price_gpu, high_price_gpu, low_price_gpu, volume_gpu, key_level_score_multiplier_gpu, identified_key_level_count_gpu, identified_key_levels_gpu, block=(1,GPU_CORE_BLOCK_SIZE,1))
    
    identified_key_level_count = np.empty_like(identified_key_level_count)
    cuda.memcpy_dtoh(identified_key_level_count, identified_key_level_count_gpu)
    print('identified_key_level_count is ' + str(identified_key_level_count))
    
    identified_key_levels = np.empty_like(identified_key_levels)
    cuda.memcpy_dtoh(identified_key_levels, identified_key_levels_gpu)

    df = pd.DataFrame(data=identified_key_levels[0:identified_key_level_count], columns=IDENTIFIED_KEY_LEVELS_COLUMNS)
    print(df)
    
    df = df[['ticker id', 'identified time id', 'key level price', 'pivot point down', 'key level type specific score']]
    df.rename(columns = {'pivot point down':'pressure up'}, inplace = True) 
    df['key level type'] = 'Pivot'

    return df
    

