import os

os.add_dll_directory(r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.1\bin")
os.add_dll_directory(r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.1\bin\x64")

import pycuda.autoinit
import pycuda.driver as cuda

print(cuda.Device(0).name(), cuda.Device(0).compute_capability())
