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

from pytoolsz.dataframe import just_load
from pathlib import Path

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
    