#  ____       _____           _
# |  _ \ _   |_   _|__   ___ | |___ ____
# | |_) | | | || |/ _ \ / _ \| / __|_  /
# |  __/| |_| || | (_) | (_) | \__ \/ /
# |_|    \__, ||_|\___/ \___/|_|___/___|
#        |___/

# Copyright (c) 2024 Sidney Zhang <zly@lyzhang.me>
# PyToolsz is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#          http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.

import pandas as pd
import polars as pl
from pathlib import Path

def getreader(dirfile:Path|str, used_by:str|None = None):
    if used_by is None :
        fna = Path(dirfile).suffix
        if fna in [".xls",".xlsx"]:
            return pl.read_excel
        else:
            return getattr(pl, "read_{}".format(fna), pl.read_csv)
    else:
        return getattr(pl, "read_{}".format(used_by))

def just_load(filepath:str, engine:str = "polars", 
              used_by:str|None = None, **kwgs) -> pl.DataFrame|pd.DataFrame:
    """load file to DataFrame"""
    rFunc = getreader(filepath, used_by)
    res = rFunc(filepath, **kwgs)
    if engine not in ["polars","pandas"]:
        raise ValueError("engine must be one of {}".format(["polars","pandas"]))
    else:
        return res.to_pandas() if engine == "pandas" else res

class DataFrame(object):
    __ENGINES = ["polars","pandas"]
    def __init__(self, filepath:str, engine:str = "polars", **kwgs) -> None:
        if engine not in DataFrame.__ENGINES:
            raise ValueError("engine must be one of {}".format(DataFrame.__ENGINES))
        self.__data = just_load(filepath, engine, **kwgs)
        self.__filepath = filepath
    def __repr__(self) -> str:
        return self.__data.__repr__()
    def __str__(self) -> str:
        return self.__data.__str__()
    def __len__(self) -> int:
        return len(self.__data)
    @property
    def shape(self) -> tuple:
        return self.__data.shape
    @property
    def columns(self) -> list:
        return self.__data.columns
    @property
    def stat(self) :
        pass
    def get(self, type:str = "polars") -> pl.DataFrame|pd.DataFrame:
        if type not in DataFrame.__ENGINES:
            raise ValueError("type must be one of {}".format(DataFrame.__ENGINES))
        return self.__data