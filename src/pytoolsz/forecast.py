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
# 模型目前支持：prophet、ARIMA。
# 这里提供预测所需要的各类方法。
# 对模型的基础理解：
# 1. ARIMA ：传统时序模型的基准模型，需要前序处理，并寻找平稳方案。
# 2. prophet ：传统时序模型的集大成者，减少前序处理程度，并提供了更多添加属性，使时序预测更准确。

from itertools import product
from pathlib import Path
from prophet import Prophet
from prophet.plot import add_changepoints_to_plot
from statsmodels.tsa.stattools import adfuller,arma_order_select_ic
from statsmodels.tsa.statespace.sarimax import SARIMAX

from pytoolsz.tsTools import tsFrame
from pytoolsz.frame import szDataFrame

import pmdarima as pm
from pmdarima import model_selection

import pandas as pd
import polars as pl
import numpy as np
from typing import Iterable

__all__ = ["is_DataFrame", "auto_orders", "simforecast"]

def is_DataFrame(obj) -> bool :
    """判断是否为 DataFrame 类型"""
    return isinstance(obj,
                      (pl.DataFrame, pd.DataFrame, tsFrame, szDataFrame))

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

class simforecast(object):
    """
    sim(ple) forecast
    """
    __all__ = ["MODES","fit","predict","plot"]
    MODES = ["prophet", "arima"]
    PROPHETKWGS = ["growth","changepoints","n_changepoints","changepoint_range",
                   "yearly_seasonality","weekly_seasonality","daily_seasonality",
                   "holidays","seasonality_mode",
                   "seasonality_prior_scale","holidays_prior_scale","changepoint_prior_scale",
                   "mcmc_samples","interval_width","uncertainty_samples",
                   "stan_backend","scaling","holidays_mode"]
    ARIMAKWGS = ["start_p","d","start_q","max_p","max_d","max_q","start_P","D","start_Q",
                 "max_P","max_D","max_Q","max_order","m","seasonal","stationary",
                 "information_criterion","alpha","test","seasonal_test","stepwise","n_jobs",
                 "start_params","trend","method","maxiter","offset_test_args",
                 "seasonal_test_args","suppress_warnings","error_action","trace","random",
                 "random_state","n_fits","return_valid_fits","out_of_sample_size","scoring",
                 "scoring_args","with_intercept","sarimax_kwargs","start_params","transformed",
                 "includes_fixed","method","method_kwargs","gls","gls_kwargs","cov_type","cov_kwds",
                 "return_params","low_memory"]
    def __init__(self, data:tsFrame|pl.DataFrame|pd.DataFrame,
                 ds:str|None = None, y:str|None = None,
                 variables:str|Iterable[str]|None = None, 
                 mode:str|None = "prophet",
                 predict_function:callable|None = None,
                 **kwgs) -> None:
        """
        预测集合 - 
            目前支持的模型有：ARIMA，SARIMAX，prophet。
        参数 : 
        mode - 选择预测模型
        """
        match mode:
            case "prophet" :
                self.__mFunc = Prophet
            case "arima" :
                self.__mFunc = pm.arima.AutoARIMA
            case None :
                if predict_function is not None :
                    self.__mFunc = predict_function
                else :
                    raise ValueError("mode or predict_function is required.")
            case _ :
                raise ValueError("mode `{}` is not supported.".foermat(mode))
        self.__mode = mode
        self.__kwargs = kwgs
        self.__model = None
        self.__fitted = False
        self.__future = None
        self.__oridata = data if isinstance(data, tsFrame) else tsFrame(data,ds,y,variables)
        self.__overdata = None
    def set_prophet_configs(self, key:str, value = None) -> None :
        """
        prophet 模型变量设定
            key等于help时，打印出prophet的帮助文档；
            否则，按照prophet文档进行设定。
        """
        if self.__mode != "prophet" :
            raise ValueError("mode is not prophet.")
        if key.lower() == "help" :
            print(Prophet.__dict__["__doc__"])
        elif key in simforecast.PROPHETKWGS :
            self.__kwargs[key] = value
        else :
            raise ValueError("key `{}` is not supported.".format(key))
    def set_autoarima_configs(self, key:str, value = None) -> None :
        if self.__mode != "arima" :
            raise ValueError("mode is not arima.")
        if key.lower() == "help" :
            print(pm.arima.AutoARIMA.__dict__['__doc__'])
        elif key in simforecast.ARIMAKWGS :
            self.__kwargs[key] = value
        else :
            raise ValueError("key `{}` is not supported.".format(key))
    def setConfigs(self, **kwgs):
        if self.__mode == "prophet" :
            for k,v in kwgs.items() :
                self.set_prophet_configs(k,v)
        elif self.__mode == "arima" :
            for k,v in kwgs.items() :
                self.set_autoarima_configs(k,v)
        else :
            self.__kwargs.update(kwgs)
    def help(self) :
        if self.__mode == "prophet" :
            self.set_prophet_configs("help")
        if self.__mode == "arima" :
            self.set_autoarima_configs("help")
        if self.__mode is None :
            print("No Help for ")
    def fit(self, cap:str|Iterable|float|None = None,
            floor:str|Iterable|float|None = None, **kwgs):
        match self.__mode:
            case "prophet" :
                mod_kwgs = {k:v for k,v in self.__kwargs.items() if k != "stan_kwgs"}
                fit_kwgs = self.__kwargs["stan_kwgs"]
            case "arima" :
                mod_kwgs = {k:v for k,v in self.__kwargs.items() if k not in [
                    "sarimax_kwargs","start_params","transformed","includes_fixed",
                    "method","method_kwargs","gls","gls_kwargs","cov_type","cov_kwds",
                    "return_params","low_memory"]}
                fit_kwgs = {k:v for k,v in self.__kwargs.items() if k in [
                    "sarimax_kwargs","start_params","transformed","includes_fixed",
                    "method","method_kwargs","gls","gls_kwargs","cov_type","cov_kwds",
                    "return_params","low_memory"]}
            case None :
                mod_kwgs = self.__kwargs
                fit_kwgs = kwgs
        self.__model = self.__mFunc(**mod_kwgs)
        if self.__mode == "prophet" :
            self.__overdata = self.__oridata.for_prophet(cap, floor)
            uX = None
        elif self.__mode == "arima" :
            self.__overdata, uX = self.__oridata.for_auto_arima(need_x=True)
        else :
            self.__overdata, uX = (self.__oridata.to_pandas(), None)
        if uX is None :
            self.__model.fit(self.__overdata, **fit_kwgs)
        else:
            self.__model.fit(self.__overdata, X=uX, **fit_kwgs)
    def predict(self, n_periods:int = 10,
                freq:str = 'D',
                include_history:bool = False,
                return_conf_int:bool = False,
                alpha:float = 0.05) :
        if self.__mode == "prophet" :
            future = self.__model.make_future_dataframe(periods=n_periods, 
                                                        freq=freq, 
                                                        include_history=include_history)
            pred = self.__model.predict(future)
            return pred
        elif self.__mode == "arima" :
            pred = self.__model.predict(n_periods, return_conf_int=return_conf_int, alpha=alpha)
            pass
        else :
            pass
    def plot(self, change_points:bool = False):
        pass

def load_model(mpath:str|Path, mode:str = "prophet") -> simforecast :
    pass