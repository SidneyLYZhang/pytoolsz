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

from pathlib import Path
from pytoolsz.dataframe import DataFrame,zipreader


TARGETNAMES = ["频道","内容","流量来源","地理位置","观看者年龄","观看者性别","日期","收入来源",
              "订阅状态","订阅来源","内容类型","播放列表","设备类型","广告类型","交易类型",
              "YouTube 产品","播放位置","操作系统","字幕","视频信息语言","是否使用翻译",
              "片尾画面元素类型","片尾画面元素","卡片类型","卡片","分享服务","频道所有权",
              "版权声明状态","播放器类型","新观看者和回访观看者","资产","观看者年龄_观看者性别"]

DATANAMES = ["表格数据","图表数据","总计"]

COMPARENAME = "（比较对象）"

def read_YouTube_zipdata(tarName:str, between_date:list[str], channelName:str,
                           dataName:str, rootpath:Path|None = None, 
                           compare:bool = False) -> DataFrame:
    filelike = "{} {}_{} {}.zip".format(tarName,*between_date,channelName)
    csvlike = "{}{}.csv".format(dataName,COMPARENAME if compare else "")
    homepath = Path(rootpath) if rootpath else Path(".").absolute()
    data = zipreader(homepath/filelike, csvlike)
    return data

def read_multiChannel(tarName:str, between_date:list[str], channelNames:list[str],
                      dataName:str, rootpath:Path|None = None, 
                      compare:bool = False, group_by:str|None = None) -> DataFrame:
    data = []
    for chs in channelNames :
        data.append(read_YouTube_zipdata(tarName, between_date, chs, 
                                         dataName, rootpath, compare))
    return data


