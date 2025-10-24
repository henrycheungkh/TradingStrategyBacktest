# -*- coding: utf-8 -*-
"""
Created on Sat Aug 21 14:56:49 2021

@author: Henry Cheung
"""

import os
import InvestmentAnalytics.Config as Config


# _path = r"D:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Tools\MSVC\14.28.29910\bin\Hostx64\x64"
_path = Config.CONFIG_BASE_CCompilerPath

if os.system("cl.exe"):
    os.environ['PATH'] += ';' + _path
if os.system("cl.exe"):
    raise RuntimeError("cl.exe still not found, path probably incorrect")