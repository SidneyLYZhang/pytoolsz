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

from typing import Self
from pathlib import Path
from PIL import Image
from tempfile import TemporaryDirectory
import win32com.client as wcc
import sys

__all__ = ["convertPPT", "PPT_longPic"]

class convertPPT(object):
    """
    win32com使用VBA的API，可从官方教程中看到：
    https://learn.microsoft.com/en-us/office/vba/api/PowerPoint.Presentation.SaveAs
    编码来源：https://my.oschina.net/zxcholmes/blog/484789
    """
    TTYPES = {
        "JPG" : 17,
        "PNG" : 18,
        "PDF" : 32,
        "XPS" : 33
    }
    __all__ = ["savetype", "trans", "close", "open"]

    def __init__(self, file:str|Path, trans:str = "JPG") -> None:
        if sys.platform != "win32":
            raise SystemError("Only support Windows system.")
        if not Path(file).exists():
            raise FileNotFoundError("File not found! Please check the file path.")
        if trans.upper() not in convertPPT.TTYPES.keys():
            raise ValueError("Save type is not supported.")
        self.__file = Path(file)
        self.__saveType = (convertPPT.TTYPES[trans.upper()], trans.upper())
        self.__inUsing = wcc.Dispatch('PowerPoint.Application')
    def __enter__(self) -> Self:
        return self
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()
    @property
    def savetype(self) -> str :
        return self.__saveType[1]
    @classmethod
    def open(cls, file:str|Path, trans:str = "JPG") -> Self :
        return cls(file, trans = trans.upper())
    def saveAs(self, saveType:str|None = None) -> None :
        if saveType not in convertPPT.TTYPES.keys():
            raise ValueError("Save type is not supported.")
        if saveType is not None:
            self.__saveType = (convertPPT.TTYPES[saveType.upper()], saveType.upper())
        else:
            self.__saveType = (convertPPT.TTYPES["JPG"], "JPG")
    def trans(self, saveto:str|Path = ".", 
              width:int|None = None) -> None :
        """
        saveto : 保存路径，默认为当前路径。
        """
        ppt = self.__inUsing.Presentations.Open(self.__file.absolute())
        if Path(saveto) == Path('.') :
            output = self.__file.absolute()
        else :
            output = Path(saveto).absolute()
        if width is not None :
            ppt.Export(output, self.__saveType[1], width)
        else:
            ppt.SaveAs(output, self.__saveType[0])
    def close(self, to_console:bool = False) -> None :
        self.__inUsing.Quit()
        if to_console :
            print("File converted successfully.")


def PPT_longPic(pptFile:str|Path, saveName:str|None = None, width:int|str|None = 700, 
                saveto:str|Path = ".") -> None :
    """
    width : 画幅宽度，可以直接指定宽度像素，也可以使用字符串数据输入百分比。
            （700； "22.1%"）
                指定为None的时候，不进行图像缩放。
    """
    if saveName :
        sType = saveName.split(".")[-1] if "." in saveName else "JPG"
        if sType.upper() not in ["JPG", "PNG"] :
            raise ValueError("Unable to save this type `{}` of image.".format(sType))
    else:
        sType = "JPG"
    with TemporaryDirectory() as tmpdirname:
        with convertPPT(pptFile, trans=sType) as ppt:
            ppt.trans(saveto=tmpdirname)
        picList = list(Path(tmpdirname).glob("*.{}".format(sType)))
        with Image.open(picList[0]) as img :
            if isinstance(width, str):
                qw = float(width[:-1])/100.0
                nwidth, nheight = (int(img.width*qw), int(img.height*qw))
            elif width is None:
                nwidth, nheight = img.size
            else:
                nwidth, nheight = (width, int(img.height*width/img.width))
            canvas = Image.new(img.mode, (nwidth, nheight * len(picList)))
        for i in range(1,len(picList)+1) :
            with Image.open(Path(tmpdirname).joinpath("幻灯片{}.{}".format(i,sType))) as img :
                new_img = img.resize((nwidth,nheight), resample=Image.Resampling.LANCZOS)
                canvas.paste(new_img, box=(0, (i-1) * nheight))
        if Path(saveto) == Path('.') :
            filepath = Path(pptFile).parent
        else :
            filepath = Path(saveto)
        if saveName :
            if '.' in saveName :
                canvas.save(filepath.joinpath(saveName))
            else:
                canvas.save(filepath.joinpath(saveName), format=sType)
        else:
            canvas.save(filepath.joinpath(Path(pptFile).stem), format=sType)


if __name__ == "__main__":
    pptfile = "./test.pptx"
    PPT_longPic(pptfile, saveto="./")