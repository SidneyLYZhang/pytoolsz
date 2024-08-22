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

from pytoolsz.frame import just_load
from pathlib import Path
from numbers import Number
from rich.markdown import Markdown
from rich.console import Console
from decimal import Decimal,ROUND_HALF_UP
from collections.abc import Iterable


import numpy as np

import shutil
import re

def covert_macadress(macadress:str, upper:bool = True) -> str:
    """
    自适应的MAC地址转换方法。
    """
    sl = len(macadress)
    if sl == 12 :
        pattern = r"(\w{2})(\w{2})(\w{2})(\w{2})(\w{2})(\w{2})"
        res = re.sub(pattern, r"\1:\2:\3:\4:\5:\6", macadress)
    elif sl == 17 :
        res = macadress.split(":")
        res = "".join(res)
    else:
        raise ValueError("macadress must be 12 or 17 characters")
    return res.upper() if upper else res.lower()

def convert_suffix(file:str, to:str = "csv") -> None :
    """
    转换文件类型到对应文件类型
    """
    file_path = Path(file)
    data = just_load(file_path)
    if file_path.suffix == '.{}'.format(to) :
        raise ValueError("file is already in {} format".format(to))
    elif file_path.suffix == '.csv' and to == 'txt' :
        shutil.copy(file_path, file_path.with_suffix('.txt'))
    elif to in ["xls","xlsx"] :
        data.write_excel(file_path.with_suffix('.{}'.format(to)))
    else:
        func = getattr(data, "write_{}".format(to), data.write_csv)
        func(file_path.with_suffix('.'+to))
    print("converted successfully!")

def youtube_datetime():
    pass

def around_right(nums:Number|None, keep_n:int = 2, 
                 null_na_handle:bool|float = False,
                 precise:bool = False) :
    """
    用于更准确的四舍五入操作。
    对于None、Null或者NAN/NA等情况，可通过null_na_handle参数进行处理。
    默认不处理。
    通过null_na_handle参数也可以指定把这些转化为指定数值。
    通过precise参数，可以启用精准四舍五入计算。
    """
    if (nums is None) or (nums is np.nan):
        if isinstance(null_na_handle, bool) :
            tNum = np.float64(0.0) if null_na_handle else nums
        else :
            tNum = np.float64(null_na_handle)
    elif nums is np.inf :
        return np.inf
    else :
        tNum = nums
    if precise :
        def decimal_round(tn:str, keep:int):
            return Decimal(tn).quantize(Decimal('0.'+'0'*keep), rounding=ROUND_HALF_UP)
        middleNum = decimal_round(str(tNum), keep_n+4)
        return np.float64(decimal_round(str(middleNum), keep_n))
    else :
        middleNum = np.around(tNum, decimals=(keep_n+4))
        return np.around(middleNum, decimals=keep_n)

def round(numbs:Iterable) -> Iterable[float] :
    
    pass

def markdown_print(text:str) -> None:
    """
    使用Markdown方式进行文本输出。
    """
    console = Console()
    console.print(Markdown(text))