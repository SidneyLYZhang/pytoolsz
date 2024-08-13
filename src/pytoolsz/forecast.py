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

# 说明：
# 预测需要做这样几件事：
# 1. 确实数据是否平稳
# 2. 处理数据，进行差分
# 3. 拟合模型
# 4. 预测
# 传统来说，平稳与否是一个时间序列预测是否可行的标志。但现在也有很多手段可以在务虚平稳条件下进行预测。
# 模型除了prophet、ARIMA，还有auto.gluon.ai和PatchTST。
# 这里提供预测所需要的各类方法。

import prophet as fp

class forecast(object):
    def __init__(self) -> None:
        pass
    def fit(self,data):
        pass
    def predict(self,data):
        pass
    def plot(self):
        pass