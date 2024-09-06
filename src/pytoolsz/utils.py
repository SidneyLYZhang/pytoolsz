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

import re

from random import randint
from rich.console import Console
from rich.highlighter import Highlighter
from rich.markdown import Markdown

__all__ = [
    "println", "print_special"
]

class RainbowHighlighter(Highlighter):
    def highlight(self, text):
        for index in range(len(text)):
            text.stylize(f"color({randint(16, 255)})", index, index + 1)

def println(text:str, color:str = "auto", 
            style:str|None = None, end:str = "\n",
            width:int|None = None) -> None:
    """带颜色的文本输出"""
    cons = Console(width=width)
    if color == "auto" :
        txt = text
    elif color == "rainbow" :
        txt = RainbowHighlighter()(text)
    else :
        txt = f"[{color}]{text}[/{color}]"
    cons.print(txt, style=style, end=end)

def print_special(data:any, mode:str = "auto", 
                  width:int|None = None) -> None :
    """特殊输出，可指定输出markdown格式。"""
    cons = Console(width=width)
    if mode == "auto" :
        cons.print(data)
    elif mode == "markdown" :
        cons.print(Markdown(data))
    elif mode == "rainbow":
        println(data, color="rainbow", width=width)
    elif re.match(r"^color-\(?[\d|a-z]+\)?$", mode):
        color = re.search("[\d|a-z]+", mode.split("-")[1]).group()
        if re.match(r"^\d+$", color) :
            color = "color({})".format(color)
        println(data, color=color, width=width)
    else:
        raise ValueError("mode must be 'auto','markdown', 'rainbow' or 'color-(color)'")