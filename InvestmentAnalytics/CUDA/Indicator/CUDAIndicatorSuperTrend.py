
import pycuda.driver as cuda
import pycuda.autoinit
# import pycuda.tools.PooledDeviceAllocation
# from pycuda.tools import PooledDeviceAllocation
import pycuda._driver as _drv

from pycuda.compiler import SourceModule
import math
import pandas as pd
import numpy as np
import InvestmentAnalytics.CUDA.CUDAPathSetting

GPU_CORE_BLOCK_SIZE = 32*32

# https://www.tradinformed.com/calculate-supertrend-indicator-using-excel/
# https://tradingtuitions.com/supertrend-indicator-excel-sheet-with-realtime-buy-sell-signals/
# http://www.freebsensetips.com/download/detail/3/Supertrend-indicator-calculation-in-excel

# def AppendListToDF(original_df, column_name, lst):
#     if isinstance(lst[0], list):
#         col_name_list = []
#         for i in range(len(lst[0])):
#             col_name_list.append(column_name+' '+str(i))
#     else:
#         col_name_list = [column_name]
#     df = pd.DataFrame(lst, columns =col_name_list)
#     # print('df for AppendListToDF for ' + column_name + ' is')
#     # print(df)
#     df['Dummy'] = 1
#     return original_df.merge(df, on='Dummy')

# def InitialiseScenarioMatrix(ticker_count, indicator_parameter_set_count, scenario_labels_dict):
def InitialiseScenarioMatrix(ticker_count, indicator_parameter_set_count):
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
    # for key in scenario_labels_dict:
    #     scenario_df = AppendListToDF(scenario_df, key, scenario_labels_dict[key])


    # # scenario_df = AppendListToDF(scenario_df, ObsPeriod, 'obs period')
    # # scenario_df = AppendListToDF(scenario_df, SharpeRatioThreshold, 'sharpe ratio threshold')
    # # scenario_df = AppendListToDF(scenario_df, ExitSharpeRatioOffset, 'exit sharpe ratio offset')
    # # scenario_df = AppendListToDF(scenario_df, StopLossPerTrade, 'stop loss')
    # # scenario_df = AppendListToDF(scenario_df, TakeProfitPerTrade, 'take profit')
    # # scenario_df = AppendListToDF(scenario_df, MaxHoldingPeriod, 'max holding period')
    scenario_df.drop(columns=['Dummy'], inplace=True)
    # # scenario_count = len(scenario_df)

    scenario_matrix = scenario_df.to_numpy().astype(np.float32)
    return scenario_matrix.copy(order="C")
    

def CUDAIndicatorSuperTrend(close_price_matrix, high_price_matrix, low_price_matrix, ParameterList):
    print('In CUDAIndicatorSuperTrend, close_price_matrix is')
    print(close_price_matrix)
    ticker_size = len(close_price_matrix)
    time_size = len(close_price_matrix[0])
    block_cutting_by_time = 0
    Parameter_size = len(ParameterList)
    print('Parameter_size is ' + str(Parameter_size))
    Parameter_matrix = np.array(ParameterList).astype(np.float32)
    print('Parameter_matrix is')
    print(Parameter_matrix)
    
    # scenario_matrix = InitialiseScenarioMatrix(ticker_size, Parameter_size, ['ticker id', 'ATR Length', 'Factor'])
    scenario_matrix = InitialiseScenarioMatrix(ticker_size, Parameter_size)
    print('scenario_matrix is ')
    print(scenario_matrix)
    scenario_count = len(scenario_matrix)
    scenario_column_count = len(scenario_matrix[0])


    close_price_matrix = close_price_matrix.T.copy(order="C")
    high_price_matrix = high_price_matrix.T.copy(order="C")
    low_price_matrix = low_price_matrix.T.copy(order="C")


    # if block_cutting_dimension == "Time Dimension":
    #     close_price_matrix = close_price_matrix.T.copy(order="C")
    #     block_cutting_by_time = 1
    #     # print('before run')
    #     indicator_matrix = np.zeros((time_size * Parameter_size, ticker_size)).astype(np.float32)
    # else:
    #     indicator_matrix = np.zeros((ticker_size * Parameter_size, time_size)).astype(np.float32)

    indicator_matrix = np.zeros((time_size * Parameter_size, ticker_size)).astype(np.float32)
    signal_matrix = np.zeros((time_size * Parameter_size, ticker_size)).astype(np.float32)
        
    
    # print('before running, len(indicator_matrix) is ' + str(len(indicator_matrix)))
    # print('before running, len(time_size) is ' + str(time_size) + ', len(ticker_size) is ' + str(ticker_size) + ', len(MA_Day_size) is ' + str(MA_Day_size))
    # print(indicator_matrix)
    first_dimension_size = len(close_price_matrix)
    second_dimension_size = len(close_price_matrix[0])

    gpu_core_block_count = math.ceil(first_dimension_size/GPU_CORE_BLOCK_SIZE) 

        
    # ticker_block_count = math.ceil(ticker_size/GPU_CORE_BLOCK_SIZE)

    # a1 = close_price_matrix
    # b = np.zeros((ticker_size, time_size))

    close_price_matrix = close_price_matrix.astype(np.float32)
    high_price_matrix = high_price_matrix.astype(np.float32)
    low_price_matrix = low_price_matrix.astype(np.float32)
    # b = b.astype(np.float32)
    
    close_price_matrix_gpu = cuda.mem_alloc(close_price_matrix.nbytes)
    cuda.memcpy_htod(close_price_matrix_gpu, close_price_matrix)
    high_price_matrix_gpu = cuda.mem_alloc(high_price_matrix.nbytes)
    cuda.memcpy_htod(high_price_matrix_gpu, high_price_matrix)
    low_price_matrix_gpu = cuda.mem_alloc(low_price_matrix.nbytes)
    cuda.memcpy_htod(low_price_matrix_gpu, low_price_matrix)
    
    indicator_matrix_gpu = cuda.mem_alloc(indicator_matrix.nbytes)
    cuda.memcpy_htod(indicator_matrix_gpu, indicator_matrix)
    basic_upperband_matrix_gpu = cuda.mem_alloc(indicator_matrix.nbytes)
    cuda.memcpy_htod(basic_upperband_matrix_gpu, indicator_matrix)
    basic_lowerband_matrix_gpu = cuda.mem_alloc(indicator_matrix.nbytes)
    cuda.memcpy_htod(basic_lowerband_matrix_gpu, indicator_matrix)
    signal_matrix_gpu = cuda.mem_alloc(indicator_matrix.nbytes)
    cuda.memcpy_htod(signal_matrix_gpu, indicator_matrix)
    
    Parameter_matrix_gpu = cuda.mem_alloc(Parameter_matrix.nbytes)
    cuda.memcpy_htod(Parameter_matrix_gpu, Parameter_matrix)
    
    scenario_matrix_gpu = cuda.mem_alloc(scenario_matrix.nbytes)
    cuda.memcpy_htod(scenario_matrix_gpu, scenario_matrix)
          

    mod = SourceModule("""
   __global__ void get_true_range(int first_dimension_size, int second_dimension_size, int GPU_CORE_BLOCK_SIZE, int gpu_core_block_count, float *close_price_matrix, float *high_price_matrix, float *low_price_matrix, float *basic_upperband_matrix, float *basic_lowerband_matrix, float *Parameter_matrix, int Parameter_size)
   {

       int time_id, ATR_Length, Parameter_index_offset;
       float Factor, true_range, avg_true_range, temp_range, basic_upperband, basic_lowerband, final_upperband, final_lowerband;

//       basic_upperband_matrix[0] = 1;
       
//       if (block_cutting_by_time == 0) {
//       } else {
         for (int k = 0; k < gpu_core_block_count; k++) {
           time_id = k * GPU_CORE_BLOCK_SIZE + threadIdx.y;
           if (time_id < first_dimension_size) {
             for (int Parameter_index = 0; Parameter_index < Parameter_size; Parameter_index++) {
               ATR_Length = (int) Parameter_matrix[Parameter_index * 2];
               Factor = Parameter_matrix[Parameter_index * 2 + 1];

//               basic_upperband_matrix[0] = Factor;
//               basic_upperband_matrix[1] = ATR_Length;

              
               if (time_id < ATR_Length ) {
                 for (int ticker_id = 0; ticker_id < second_dimension_size; ticker_id++) {
                   Parameter_index_offset = Parameter_index * first_dimension_size * second_dimension_size + time_id * second_dimension_size + ticker_id;
//                   basic_upperband_matrix[Parameter_index_offset] = 0;
//                   basic_lowerband_matrix[Parameter_index_offset] = 0;
                 }
               } else {
                 for (int ticker_id = 0; ticker_id < second_dimension_size; ticker_id++) {
                   Parameter_index_offset = Parameter_index * first_dimension_size * second_dimension_size + ticker_id;
                   avg_true_range = 0;
                   for (int obs_time_id = time_id - ATR_Length + 1 ; obs_time_id <= time_id; obs_time_id++ ) {
                     true_range = high_price_matrix[obs_time_id * second_dimension_size + ticker_id] - low_price_matrix[obs_time_id * second_dimension_size + ticker_id];
                     temp_range = abs(high_price_matrix[obs_time_id * second_dimension_size + ticker_id] - close_price_matrix[(obs_time_id - 1) * second_dimension_size + ticker_id]);
                     if (temp_range > true_range) {
                       true_range = temp_range;
                     }
                     temp_range = abs(low_price_matrix[obs_time_id * second_dimension_size + ticker_id] - close_price_matrix[(obs_time_id - 1) * second_dimension_size + ticker_id]);
                     if (temp_range > true_range) {
                       true_range = temp_range;
                     }
                     avg_true_range = avg_true_range + true_range;
                   }
                   avg_true_range = avg_true_range / ATR_Length;
                   if (avg_true_range == 0) {
                     avg_true_range = 0.000001;
                   }
                   basic_upperband_matrix[Parameter_index_offset + time_id * second_dimension_size] = (high_price_matrix[time_id * second_dimension_size + ticker_id] + low_price_matrix[time_id * second_dimension_size + ticker_id]) / 2 + avg_true_range * Factor;
                   basic_lowerband_matrix[Parameter_index_offset + time_id * second_dimension_size] = (high_price_matrix[time_id * second_dimension_size + ticker_id] + low_price_matrix[time_id * second_dimension_size + ticker_id]) / 2 - avg_true_range * Factor;
//                   basic_upperband_matrix[Parameter_index_offset + time_id * second_dimension_size] = (high_price_matrix[time_id * second_dimension_size + ticker_id] + low_price_matrix[time_id * second_dimension_size + ticker_id]) / 2;
//                   basic_lowerband_matrix[Parameter_index_offset + time_id * second_dimension_size] = avg_true_range;
//                   basic_upperband_matrix[Parameter_index_offset + time_id * second_dimension_size] = time_id;
//                   basic_lowerband_matrix[Parameter_index_offset + time_id * second_dimension_size] = time_id;
                 }
               }
             }
           }
         }
//       }
   }
   """)

    func = mod.get_function("get_true_range")
    func(np.int32(first_dimension_size), np.int32(second_dimension_size), np.int32(GPU_CORE_BLOCK_SIZE), np.int32(gpu_core_block_count), close_price_matrix_gpu, high_price_matrix_gpu, low_price_matrix_gpu, basic_upperband_matrix_gpu, basic_lowerband_matrix_gpu, Parameter_matrix_gpu, np.int32(Parameter_size), block=(1,GPU_CORE_BLOCK_SIZE,1))
   # __global__ void get_true_range(int block_cutting_by_time, int first_dimension_size, int second_dimension_size, int GPU_CORE_BLOCK_SIZE, int gpu_core_block_count, float *close_price_matrix, float *high_price_matrix, float *low_price_matrix, float *basic_upperband_matrix, float *basic_lowerband_matrix, int *Parameter_matrix, int Parameter_size)

    # basic_upperband_matrix = np.empty_like(indicator_matrix)
    # cuda.memcpy_dtoh(basic_upperband_matrix, basic_upperband_matrix_gpu)
    # basic_lowerband_matrix = np.empty_like(indicator_matrix)
    # cuda.memcpy_dtoh(basic_lowerband_matrix, basic_lowerband_matrix_gpu)
    
    # print('basic_upperband_matrix is with dimension ' + str(len(basic_upperband_matrix)) + ' x ' + str(len(basic_upperband_matrix[0])))
    # print(basic_upperband_matrix)
    # print('basic_lowerband_matrix is with dimension ' + str(len(basic_lowerband_matrix)) + ' x ' + str(len(basic_lowerband_matrix[0])))
    # print(basic_lowerband_matrix)
    
    # full_matrix = np.concatenate((high_price_matrix, low_price_matrix), axis=1)
    # full_matrix = np.concatenate((full_matrix, close_price_matrix), axis=1)
    # full_matrix = np.concatenate((full_matrix, basic_upperband_matrix), axis=1)
    # full_matrix = np.concatenate((full_matrix, basic_lowerband_matrix), axis=1)

    # # # pd.DataFrame(close_price_matrix).to_csv(r'G:\TradeAnalysisProject\temp\close_price_matrix.csv', index=False)
    # # # pd.DataFrame(high_price_matrix).to_csv(r'G:\TradeAnalysisProject\temp\high_price_matrix.csv', index=False)
    # # # pd.DataFrame(low_price_matrix).to_csv(r'G:\TradeAnalysisProject\temp\low_price_matrix.csv', index=False)
    # # # pd.DataFrame(basic_lowerband_matrix).to_csv(r'G:\TradeAnalysisProject\temp\basic_lowerband_matrix.csv', index=False)
    # # # pd.DataFrame(basic_upperband_matrix).to_csv(r'G:\TradeAnalysisProject\temp\basic_upperband_matrix.csv', index=False)
    # pd.DataFrame(full_matrix).to_csv(r'G:\TradeAnalysisProject\temp\full_matrix.csv', index=False)
    
    # print('size of cuda memory is ' + str(cuda.__len__()))
    # print('size of cuda memory is ' + str(PooledDeviceAllocation.__len__()))
    
    # DeviceMemoryPool = _drv.DeviceMemoryPool
    # print('size of cuda memory is ' + str(DeviceMemoryPool.active_bytes))
    
    

    # print('size of basic_upperband_matrix_gpu is ' + str(len(basic_upperband_matrix_gpu)))

    mod = SourceModule("""
    __global__ void get_indicator(int first_dimension_size, int second_dimension_size, int scenario_count, int GPU_CORE_BLOCK_SIZE, int gpu_core_block_count, float *scenario_matrix, float *close_price_matrix, float *high_price_matrix, float *low_price_matrix, float *indicator_matrix, float *signal_matrix, float *basic_upperband_matrix, float *basic_lowerband_matrix, float *Parameter_matrix, int Parameter_size)
    {
        int time_id, ATR_Length, scenario_id, scenario_id_offset, ticker_id, parameter_set_id;
        float Factor, true_range, avg_true_range, temp_range, final_upperband, final_lowerband, prior_final_upperband, prior_final_lowerband, price_sum, price_diff;
          for (int k = 0; k < gpu_core_block_count; k++) {
            scenario_id = k * GPU_CORE_BLOCK_SIZE + threadIdx.y;
            if (scenario_id < scenario_count) {
              scenario_id_offset = scenario_id * 2;
              ticker_id = (int) scenario_matrix[scenario_id_offset];
              parameter_set_id = (int) scenario_matrix[scenario_id_offset + 1];
              ATR_Length = (int) Parameter_matrix[parameter_set_id * 2];
              Factor = Parameter_matrix[parameter_set_id * 2 + 1];
                for (int time_id = 0; time_id < ATR_Length; time_id++) {
                  for (int ticker_id = 0; ticker_id < second_dimension_size; ticker_id++) {
                    indicator_matrix[parameter_set_id * first_dimension_size * second_dimension_size + time_id * second_dimension_size + ticker_id] = 0;
                  }
                }
    
                prior_final_upperband = 0;
                prior_final_lowerband = 0;


                  for (int time_id = ATR_Length; time_id < first_dimension_size; time_id++) {
                
                    if (basic_upperband_matrix[parameter_set_id * first_dimension_size * second_dimension_size + time_id * second_dimension_size + ticker_id] < prior_final_upperband || close_price_matrix[(time_id) * second_dimension_size + ticker_id] > prior_final_upperband) {
                      final_upperband = basic_upperband_matrix[parameter_set_id * first_dimension_size * second_dimension_size + time_id * second_dimension_size + ticker_id];
                    } else {
                      final_upperband = prior_final_upperband;
                    }

                    if (basic_lowerband_matrix[parameter_set_id * first_dimension_size * second_dimension_size + time_id * second_dimension_size + ticker_id] > prior_final_lowerband || close_price_matrix[(time_id) * second_dimension_size + ticker_id] < prior_final_lowerband) {
                      final_lowerband = basic_lowerband_matrix[parameter_set_id * first_dimension_size * second_dimension_size + time_id * second_dimension_size + ticker_id];
                    } else {
                      final_lowerband = prior_final_lowerband;
                    }

                    if (signal_matrix[parameter_set_id * first_dimension_size * second_dimension_size + (time_id - 1) * second_dimension_size + ticker_id] <= 0 && close_price_matrix[time_id * second_dimension_size + ticker_id] > prior_final_upperband && prior_final_upperband != 0) {
                      signal_matrix[parameter_set_id * first_dimension_size * second_dimension_size + time_id * second_dimension_size + ticker_id] = 1;
                    } else if (signal_matrix[parameter_set_id * first_dimension_size * second_dimension_size + (time_id - 1) * second_dimension_size + ticker_id] >= 0 && close_price_matrix[time_id * second_dimension_size + ticker_id] < prior_final_lowerband && prior_final_lowerband != 0) {
                      signal_matrix[parameter_set_id * first_dimension_size * second_dimension_size + time_id * second_dimension_size + ticker_id] = -1;
                    } else {
                      signal_matrix[parameter_set_id * first_dimension_size * second_dimension_size + time_id * second_dimension_size + ticker_id] = signal_matrix[parameter_set_id * first_dimension_size * second_dimension_size + (time_id - 1) * second_dimension_size + ticker_id];
                    }
                    
                    if (signal_matrix[parameter_set_id * first_dimension_size * second_dimension_size + time_id * second_dimension_size + ticker_id] > 0) {
                      indicator_matrix[parameter_set_id * first_dimension_size * second_dimension_size + time_id * second_dimension_size + ticker_id] = final_lowerband;
                    } else if (signal_matrix[parameter_set_id * first_dimension_size * second_dimension_size + time_id * second_dimension_size + ticker_id] < 0) {
                      indicator_matrix[parameter_set_id * first_dimension_size * second_dimension_size + time_id * second_dimension_size + ticker_id] = final_upperband;
                    }
                    
                    prior_final_upperband = final_upperband;
                    prior_final_lowerband = final_lowerband;

                  }

            }
          }
    }
    """)

    func = mod.get_function("get_indicator")
    func(np.int32(first_dimension_size), np.int32(second_dimension_size), np.int32(scenario_count), np.int32(GPU_CORE_BLOCK_SIZE), np.int32(gpu_core_block_count), scenario_matrix_gpu, close_price_matrix_gpu, high_price_matrix_gpu, low_price_matrix_gpu, indicator_matrix_gpu, signal_matrix_gpu, basic_upperband_matrix_gpu, basic_lowerband_matrix_gpu, Parameter_matrix_gpu, np.int32(Parameter_size), block=(1,GPU_CORE_BLOCK_SIZE,1))
    # __global__ void get_indicator(int block_cutting_by_time, int first_dimension_size, int second_dimension_size, int scenario_count, int GPU_CORE_BLOCK_SIZE, int gpu_core_block_count, float *close_price_matrix, float *high_price_matrix, float *low_price_matrix, float *indicator_matrix, float *signal_matrix, float *basic_upperband_matrix, float *basic_lowerband_matrix, float *Parameter_matrix, int Parameter_size)


    indicator_matrix = np.empty_like(indicator_matrix)
    cuda.memcpy_dtoh(indicator_matrix, indicator_matrix_gpu)
    signal_matrix = np.empty_like(indicator_matrix)
    cuda.memcpy_dtoh(signal_matrix, signal_matrix_gpu)

    # full_matrix2 = np.concatenate((full_matrix, indicator_matrix), axis=1)
    # full_matrix2 = np.concatenate((full_matrix2, signal_matrix), axis=1)
    # pd.DataFrame(full_matrix2).to_csv(r'G:\TradeAnalysisProject\temp\full_matrix2.csv', index=False)

    
    result_list = []
     # single_block_size = first_dimension_size * second_dimension_size
    
     # print('len(indicator_matrix) is ' + str(len(indicator_matrix)) + ', first_dimension_size is ' + str(first_dimension_size) + ', second_dimension_size is ' + str(second_dimension_size))
    
    for i in range(Parameter_size):
     # if block_cutting_dimension == "Time Dimension":
     # x = indicator_matrix[i*first_dimension_size:(i+1)*first_dimension_size].T.copy(order="C")
     # print('for i = ' + str(i))
     # print(x)
    
        result_list.append(indicator_matrix[i*first_dimension_size:(i+1)*first_dimension_size].T.copy(order="C"))
     # else:
     #     result_list.append(indicator_matrix[i*first_dimension_size:(i+1)*first_dimension_size])
     # print('len(result_list) is ' + str(len(result_list)))
    
    
    signal_list = []
     # single_block_size = first_dimension_size * second_dimension_size
    
     # print('len(indicator_matrix) is ' + str(len(indicator_matrix)) + ', first_dimension_size is ' + str(first_dimension_size) + ', second_dimension_size is ' + str(second_dimension_size))
    
    for i in range(Parameter_size):
     # if block_cutting_dimension == "Time Dimension":
     # x = indicator_matrix[i*first_dimension_size:(i+1)*first_dimension_size].T.copy(order="C")
     # print('for i = ' + str(i))
     # print(x)
    
        signal_list.append(signal_matrix[i*first_dimension_size:(i+1)*first_dimension_size].T.copy(order="C"))
     # else:
     #     signal_list.append(signal_matrix[i*first_dimension_size:(i+1)*first_dimension_size])
     # print('len(result_list) is ' + str(len(result_list)))
    
    scenario_matrix_gpu.free()
    close_price_matrix_gpu.free()
    high_price_matrix_gpu.free()
    low_price_matrix_gpu.free()
    indicator_matrix_gpu.free()
    signal_matrix_gpu.free()
    basic_upperband_matrix_gpu.free()
    basic_lowerband_matrix_gpu.free()
    Parameter_matrix_gpu.free()
    
    return result_list, signal_list