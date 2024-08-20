#  ____       _____           _
# |  _ \ _   |_   _|__   ___ | |___ ____
# | |_) | | | || |/ _ \ / _ \| / __|_  /
# |  __/| |_| || | (_) | (_) | \__ \/ /
# |_|    \__, ||_|\___/ \___/|_|___/___|
#        |___/
#
# Copyright (c) 2024 Sidney Zhang <zly@lyzhang.me>
# PyToolsz is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#          http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.

# 说明：
# 预测需要做这样几件事：
# 1. 确实数据是否平稳
# 2. 处理数据，进行差分
# 3. 拟合模型
# 4. 预测
# 传统来说，平稳与否是一个时间序列预测是否可行的标志。但现在也有很多手段可以在务虚平稳条件下进行预测。
# 模型除了prophet、ARIMA，还有auto.gluon.ai和PatchTST。
# 这里提供预测所需要的各类方法。
# 对模型的基础理解：
# 1. ARIMA ：传统时序模型的基准模型，需要前序处理，并寻找平稳方案。
# 2. prophet ：传统时序模型的集大成者，减少前序处理程度，并提供了更多添加属性，使时序预测更准确。
# 3. PatchTST ：基于DNN的模型，是单纯神经网络方法优化的结果，在时间序列预测中也有较为优异的表现。
# 4. auto.gluon.ai ：在预训练模型中表现出色，使用LLM类方法训练的Transformer模型。

from itertools import product
from pathlib import Path
from prophet import Prophet
from prophet.plot import add_changepoints_to_plot
from statsmodels.tsa.stattools import adfuller,arma_order_select_ic
from statsmodels.tsa.statespace.sarimax import SARIMAX

import pandas as pd
import numpy as np


def auto_orders(data:pd.Series, diff_max:int = 40, 
                use_log:bool = False) -> tuple:
    """自动选择合适时序特征"""
    tdt = np.log(data) if use_log else data
    tmax = len(tdt) if diff_max > len(tdt) else diff_max
    for i in range(1,tmax+1):
        temp = tdt.diff(i).dropna()
        if any((temp == np.inf).tolist()):
            temp[temp == np.inf] = 0.0
        adf = adfuller(temp)
        if adf[1] < 0.05:
            d = i
            break
    bpq = []
    for i in ["n","c"]:
        tmp = arma_order_select_ic(tdt, ic=['aic','bic','hqic'])
        bpq.extend([
            tmp["aic_min_order"],
            tmp["bic_min_order"],
            tmp["hqic_min_order"],
        ])
    p = np.argmax(np.bincount(np.array(bpq).T[0]))
    q = np.argmax(np.bincount(np.array(bpq).T[1]))
    x = np.fft.fft(tdt)
    xf = np.linspace(0.0,0.5,len(tdt)//2)
    dx = xf[np.argmax(np.abs(x[1:(len(tdt)//2)]))]
    s = 0 if dx == 0.0 else 1//dx
    if s == 0 :
        bP,bD,bQ = (0,0,0)
    else:
        Pl = list(range(0,p+1))
        bD = 1
        Ql = list(range(0,q+1))
        lPDQl = list(product(Pl,[bD],Ql,[s]))
        PDQtrend = product(lPDQl,['n',"c",'t','ct'])
        aic_min = 100000
        for ix in PDQtrend:
            model = SARIMAX(tdt,order=(p,d,d),
                            seasonal_order=ix[0],
                            trend=ix[1]).fit(disp=False)
            aic = model.aic
            if aic < aic_min:
                aic_min = aic
                bP,bD,bQ,_ = ix[0]
                bT = ix[1]
    return ((p,d,q),(bP,bD,bQ,int(s)),bT)

class forecast(object):
    MODES = ["arima","prophet","patchtst","autogluon"]
    def __init__(self, mode:str = "prophet", 
                 orders:tuple|bool = False, use_log:bool = False, 
                 **kwgs) -> None:
        """
        预测集合 - 
            目前支持的模型有：ARIMA，prophet，patchtst，autogluon。
        参数 : 
        mode - 选择预测模型
        diff - 用于差分选择，如果为True，则进行自动选择差分，默认为False；
               指定为一个整数值，则按此进行指定的差分阶数进行计算。
        """
        if mode not in forecast.MODES:
            raise ValueError("mode must be one of {}".format(forecast.MODES))
        self.__mode = mode
        if isinstance(orders,bool):
            if orders :
                self.__diff_order = -1
            else:
                self.__diff_order = 0
        else:
            self.__diff_order = orders
        self.__kwargs = kwgs
        if mode == "prophet":
            self.__mFunc = Prophet
        elif mode == "arima" :
            self.__mFunc = SARIMAX
        elif mode == "patchtst" :
            self.__mFunc = None
        else:
            self.__mFunc = None
        self.__model = None
        self.__fitted = False
        self.__future = None
        self.__oridata = None
        self.__overdata = None
    def fit(self,data):
        pass
    def predict(self,data):
        pass
    def plot(self, change_points:bool = False):
        pass

def load_model(mpath:str|Path, mode:str = "prophet") -> forecast :
    pass