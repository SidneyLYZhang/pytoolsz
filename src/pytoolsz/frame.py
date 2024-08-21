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
from zipfile import ZipFile
from os import stat_result
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Self
from rich import print


def getreader(dirfile:Path|str, used_by:str|None = None):
    if used_by is None :
        fna = Path(dirfile).suffix
        if fna in [".xls",".xlsx"]:
            return pl.read_excel
        else:
            return getattr(pl, "read_{}".format(fna), pl.read_csv)
    else:
        return getattr(pl, "read_{}".format(used_by))

def just_load(filepath:str|Path, engine:str = "polars", 
              used_by:str|None = None, **kwgs) -> pl.DataFrame|pd.DataFrame:
    """load file to DataFrame"""
    rFunc = getreader(filepath, used_by)
    res = rFunc(Path(filepath), **kwgs)
    if engine not in ["polars","pandas"]:
        raise ValueError("engine must be one of {}".format(["polars","pandas"]))
    else:
        return res.to_pandas() if engine == "pandas" else res

class szDataFrame(object):
    __ENGINES = ["polars","pandas"]
    def __init__(self, filepath:str|None, engine:str = "polars", 
                 from_data:pl.DataFrame|pd.DataFrame|None = None, **kwgs) -> None:
        if engine not in szDataFrame.__ENGINES:
            raise ValueError("engine must be one of {}".format(szDataFrame.__ENGINES))
        if from_data is None :
            self.__data = just_load(filepath, engine, **kwgs)
        else:
            if isinstance(from_data, pl.DataFrame):
                self.__data = from_data
            else:
                self.__data = pl.from_pandas(from_data)
        self.__filepath = Path(filepath) if filepath else None
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
    def stat(self) -> stat_result|None:
        if self.__filepath is None:
            res = None
        else :
            res = self.__filepath.stat()
        return res
    def get(self, type:str = "polars") -> pl.DataFrame|pd.DataFrame:
        if type not in szDataFrame.__ENGINES:
            raise ValueError("type must be one of {}".format(szDataFrame.__ENGINES))
        return self.__data if type == "polars" else self.__data.to_pandas()
    def convert(self, to:str) -> any:
        funx = getattr(self.__data, "to_{}".format(to), None)
        if funx is None:
            raise ValueError("Don't have this convert method!")
        return funx()
    def append(self, other:Self) -> Self:
        data = self.__data.vstack(other.get())
        return szDataFrame(filepath=self.__filepath, from_data=data)
    def into_timeseries(self, date:str, value:str) -> pd.DataFrame :
        return self.__data.set_index(date).to_pandas()[value]
    def into_training(self, values:list[str], target:str, 
                      index:str|None = None, into_ts:bool = False,
                      N_test:int = 10) -> pd.DataFrame :
        pass


def zipreader(zipFilepath:Path|str, subFile:str, **kwgs) -> szDataFrame:
    with TemporaryDirectory() as tmpdirname:
        with ZipFile(Path(zipFilepath), "r") as teZip:
            teZip.extractall(path = tmpdirname)
            subFiles = teZip.namelist()
        if subFile not in subFiles:
            raise ValueError("'{}' not in zip-file({})!".format(subFile,zipFilepath))
        return szDataFrame(Path(tmpdirname)/subFile, **kwgs)

if __name__ == "__main__":
    rootpath = Path(__file__).absolute().parent.parent
    data = zipreader(rootpath/"datasets/iris/iris.zip",
                     "iris.data")
    print(data)