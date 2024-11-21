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

# 用来处理时间序列的相关工具
# 1. 时间序列数据框
# 2. 简单的时间数据计算

import pandas as pd
import polars as pl

import matplotlib.pyplot as plt

from collections.abc import Iterable
from pytoolsz.frame import szDataFrame
from pytoolsz.utils import isSubset

class tsFrame(object):
    def __init__(self, data:pl.DataFrame|pd.DataFrame|szDataFrame,
                 dt:str|Iterable, variable:str, 
                 covariates:str|Iterable[str]|None = None) -> None:
        self.__data = data if isinstance(data, szDataFrame) else szDataFrame(from_data=data)
        self.__data = self.__data.to_polars()
        if dt in self.__data.columns:
            self.__dt = dt
            self.__data = self.__data.with_column(pl.col(dt).cast(pl.Date)).sort(self.__dt)
        else:
            raise ValueError(f"{dt} is not a column in data")
        if variable in self.__data.columns:
            self.__y = variable
        else:
            raise ValueError(f"{variable} is not a column in data")
        if isinstance(covariates, str) :
            if covariates in self.__data.columns :
                self.__variables = [covariates]
            else :
                raise ValueError(f"{covariates} is not a column in data")
        elif isSubset(self.__data.columns, covariates) :
            self.__variables = covariates
        else :
            raise ValueError(f"{covariates} is not a subset of data-columns")
    def for_prophet(self) -> pd.DataFrame :
        res = self.__data.select([self.__dt, self.__y]).to_pandas()
        res.columns = ["ds","y"]
        return res
    def plot(self) -> None :
        self.__data.plot(x=self.__dt, y=self.__y)
        plt.show()